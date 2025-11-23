"""Alternative GUI entry that enables drag-and-drop via tkinterdnd2 when available.

This file provides `run_gui_dnd()` which will use `TkinterDnD.Tk()` as the root
and register the inputs listbox as a drop target for files. It falls back to
normal Tk if tkinterdnd2 is not installed and will show an informative message.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import threading
import queue
from pathlib import Path

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

from .core import collect_files, create_zip


class DnDGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(padx=10, pady=10, fill='both', expand=True)
        self._queue = queue.Queue()
        self._cancel_event = threading.Event()
        self._worker_thread = None
        self.create_widgets()
        self._poll_queue()

    def create_widgets(self):
        tk.Label(self, text='Drag files/folders here or use the buttons').pack(anchor='w')
        self.inputs_lb = tk.Listbox(self, width=80, height=8, selectmode='extended')
        self.inputs_lb.pack(fill='both', expand=True)

        bframe = tk.Frame(self)
        bframe.pack(fill='x')
        tk.Button(bframe, text='Add Files', command=self.add_files).pack(side='left')
        tk.Button(bframe, text='Add Folder', command=self.add_folder).pack(side='left')
        tk.Button(bframe, text='Remove', command=self.remove_selected).pack(side='left')

        if DND_AVAILABLE:
            try:
                self.inputs_lb.drop_target_register(DND_FILES)
                self.inputs_lb.dnd_bind('<<Drop>>', self._on_drop)
            except Exception:
                pass
        else:
            tk.Label(self, text='(Install tkinterdnd2 to enable OS drag-and-drop)').pack(anchor='w')

        out_frame = tk.Frame(self)
        out_frame.pack(fill='x', pady=6)
        self.output_var = tk.StringVar()
        tk.Entry(out_frame, textvariable=self.output_var).pack(side='left', fill='x', expand=True)
        tk.Button(out_frame, text='Browse', command=self.save_as).pack(side='left')

        ctl = tk.Frame(self)
        ctl.pack(fill='x')
        self.start_btn = tk.Button(ctl, text='Start', command=self.start)
        self.start_btn.pack(side='left')
        self.cancel_btn = tk.Button(ctl, text='Cancel', command=self.cancel, state='disabled')
        self.cancel_btn.pack(side='left')

        self.progress = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', pady=6)
        self.status = tk.Label(self, text='Idle')
        self.status.pack(anchor='w')

        self.log = tk.Text(self, height=8)
        self.log.pack(fill='both', expand=True)

    def add_files(self):
        paths = filedialog.askopenfilenames()
        for p in paths:
            self.inputs_lb.insert('end', p)

    def add_folder(self):
        p = filedialog.askdirectory()
        if p:
            self.inputs_lb.insert('end', p)

    def remove_selected(self):
        sel = list(self.inputs_lb.curselection())
        for i in reversed(sel):
            self.inputs_lb.delete(i)

    def save_as(self):
        p = filedialog.asksaveasfilename(defaultextension='.zip', filetypes=[('Zip files', '*.zip')])
        if p:
            self.output_var.set(p)

    def start(self):
        inputs = list(self.inputs_lb.get(0, 'end'))
        output = self.output_var.get().strip()
        if not inputs:
            messagebox.showerror('Error', 'No inputs selected')
            return
        if not output:
            messagebox.showerror('Error', 'Please select output path')
            return

        self.start_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.log.delete('1.0', 'end')
        self.status.config(text='Starting...')
        self.progress['value'] = 0
        self._cancel_event.clear()

        def worker():
            try:
                files = collect_files(inputs, True, [], False)
                total = len(files)
                self._queue.put(('total', total))

                def progress_cb(total, done, current):
                    self._queue.put(('progress', total, done, str(current)))

                create_zip(output, files, 6, True, password=None, progress_callback=progress_cb, cancel_event=self._cancel_event)
                self._queue.put(('done', 'Archive created'))
            except Exception as e:
                self._queue.put(('error', str(e)))

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def cancel(self):
        if messagebox.askyesno('Cancel', 'Cancel operation?'):
            self._cancel_event.set()
            self.log.insert('end', 'Cancel requested\n')
            self.cancel_btn.config(state='disabled')

    def _on_drop(self, event):
        try:
            parts = self.master.tk.splitlist(event.data)
        except Exception:
            parts = [p.strip() for p in event.data.split() if p.strip()]
        for p in parts:
            p = p.strip('{}')
            self.inputs_lb.insert('end', p)

    def _poll_queue(self):
        try:
            while True:
                item = self._queue.get_nowait()
                if item[0] == 'total':
                    total = item[1]
                    self.progress['maximum'] = total
                    self.log.insert('end', f'Total files: {total}\n')
                elif item[0] == 'progress':
                    _, total, done, current = item
                    self.progress['value'] = done
                    self.status.config(text=f'Adding {done}/{total}: {Path(current).name}')
                    self.log.insert('end', f'Added: {current}\n')
                    self.log.see('end')
                elif item[0] == 'done':
                    self.status.config(text=item[1])
                    messagebox.showinfo('Done', item[1])
                    self.start_btn.config(state='normal')
                    self.cancel_btn.config(state='disabled')
                elif item[0] == 'error':
                    self.status.config(text='Error')
                    messagebox.showerror('Error', item[1])
                    self.log.insert('end', f'Error: {item[1]}\n')
                    self.start_btn.config(state='normal')
                    self.cancel_btn.config(state='disabled')
        except queue.Empty:
            pass
        finally:
            self.after(200, self._poll_queue)


def run_gui_dnd():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    root.title('Zipper (Drag & Drop)')
    root.geometry('800x500')
    app = DnDGUI(master=root)
    app.mainloop()


if __name__ == '__main__':
    run_gui_dnd()
