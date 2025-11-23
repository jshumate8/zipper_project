"""Simple Tkinter GUI for the zipper package.

Provides a small UI to select files/folders, pick an output .zip, and
run zipping in a background thread. Exposes `run_gui()` for the smoke
test used earlier.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue

from .core import collect_files, create_zip


class ZipperGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._q = queue.Queue()
        self._worker = None
        self._cancel_event = threading.Event()
        self.create_widgets()

    def create_widgets(self):
        # Inputs list
        lbl = tk.Label(self, text="Inputs")
        lbl.grid(row=0, column=0, sticky="w")

        self.listbox = tk.Listbox(self, width=60, height=8)
        self.listbox.grid(row=1, column=0, columnspan=4, sticky="nsew")

        btn_add = tk.Button(self, text="Add Files...", command=self.add_files)
        btn_add.grid(row=2, column=0, sticky="w", pady=(6, 0))

        btn_add_dir = tk.Button(self, text="Add Folder...", command=self.add_folder)
        btn_add_dir.grid(row=2, column=1, sticky="w", pady=(6, 0))

        btn_remove = tk.Button(self, text="Remove", command=self.remove_selected)
        btn_remove.grid(row=2, column=2, sticky="w", pady=(6, 0))

        # Output
        out_lbl = tk.Label(self, text="Output .zip")
        out_lbl.grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.output_var = tk.StringVar()
        out_entry = tk.Entry(self, textvariable=self.output_var, width=50)
        out_entry.grid(row=3, column=1, columnspan=2, sticky="w", pady=(10, 0))
        out_btn = tk.Button(self, text="Browse...", command=self.browse_output)
        out_btn.grid(row=3, column=3, sticky="w", pady=(10, 0))

        # Progress and controls
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=4, sticky="we", pady=(10, 0))

        self.status_var = tk.StringVar(value="Idle")
        status_lbl = tk.Label(self, textvariable=self.status_var)
        status_lbl.grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self.start_btn = tk.Button(self, text="Start", command=self.start)
        self.start_btn.grid(row=5, column=3, sticky="e", pady=(6, 0))

        # Configure grid resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select files to add")
        for p in paths:
            if p not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, p)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder to add")
        if not folder:
            return
        files = collect_files([folder], recurse=True)
        for f in files:
            s = str(Path(f))
            if s not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, s)

    def remove_selected(self):
        sels = list(self.listbox.curselection())
        for i in reversed(sels):
            self.listbox.delete(i)

    def browse_output(self):
        out = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if out:
            self.output_var.set(out)

    def start(self):
        if self._worker and self._worker.is_alive():
            messagebox.showinfo("Zipper", "A job is already running")
            return

        files = list(self.listbox.get(0, tk.END))
        if not files:
            messagebox.showwarning("Zipper", "No input files selected")
            return
        out = self.output_var.get().strip()
        if not out:
            messagebox.showwarning("Zipper", "No output path selected")
            return

        # reset progress
        self.progress['value'] = 0
        self.status_var.set("Starting...")
        self._cancel_event.clear()

        # start worker thread
        self._worker = threading.Thread(target=self._worker_run, args=(files, out), daemon=True)
        self._worker.start()
        self.after(100, self._poll_queue)

    def _worker_run(self, files, out):
        try:
            # `create_zip` expects a list of (Path(src), Path(arcname)) tuples.
            from pathlib import Path as _P
            files_for_zip = []
            for f in files:
                p = _P(f)
                files_for_zip.append((p, _P(p.name)))

            def progress_callback(total_count, done, current_path=None):
                # create_zip calls progress_callback(total, done, src)
                self._q.put(("progress", done, total_count, str(current_path)))

            create_zip(out, files_for_zip, progress_callback=progress_callback, cancel_event=self._cancel_event)
            self._q.put(("done", None))
        except Exception as e:
            self._q.put(("error", str(e)))

    def _poll_queue(self):
        try:
            while True:
                item = self._q.get_nowait()
                kind = item[0]
                if kind == "progress":
                    _, done, total_count, message = item
                    if total_count:
                        self.progress['maximum'] = total_count
                        self.progress['value'] = done
                        self.status_var.set(message or f"{done}/{total_count}")
                elif kind == "done":
                    self.status_var.set("Done")
                    messagebox.showinfo("Zipper", "Archive created successfully")
                elif kind == "error":
                    _, err = item
                    self.status_var.set("Error")
                    messagebox.showerror("Zipper", f"Error: {err}")
        except queue.Empty:
            # continue polling if worker is alive
            if self._worker and self._worker.is_alive():
                self.after(100, self._poll_queue)
            else:
                # make sure final state is shown
                if self._worker:
                    self.status_var.set("Idle")


def run_gui():
    """Run the GUI (convenience entrypoint used by smoke tests)."""
    root = tk.Tk()
    root.title("Zipper")
    app = ZipperGUI(master=root)
    root.geometry("700x400")
    root.mainloop()


__all__ = ["ZipperGUI", "run_gui"]
