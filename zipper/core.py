import zipfile
from pathlib import Path
import fnmatch
import sys


def collect_files(inputs, recurse, exclude_patterns, include_hidden):
    results = []
    for inp in inputs:
        p = Path(inp)
        if not p.exists():
            raise FileNotFoundError(f"Input not found: {inp}")

        if p.is_dir():
            iterator = p.rglob('*') if recurse else p.iterdir()
            for f in iterator:
                if not f.is_file():
                    continue
                if not include_hidden and any(part.startswith('.') for part in f.relative_to(p).parts):
                    continue
                rel = f.relative_to(p.parent)
                rel_str = str(rel.as_posix())
                if any(fnmatch.fnmatch(rel_str, pat) for pat in exclude_patterns):
                    continue
                results.append((f, rel))
        else:
            rel = Path(p.name)
            if any(fnmatch.fnmatch(str(rel), pat) for pat in exclude_patterns):
                continue
            results.append((p, rel))

    return results


def create_zip(output, files, compresslevel=9, verbose=False, password=None, progress_callback=None, cancel_event=None):
    """Create a zip archive.

    - `files`: list of (Path(src), Path(arcname))
    - `password`: if provided, attempt to create AES-encrypted zip using `pyzipper`.
    - `progress_callback`: optional callable called as progress_callback(total, done, current_path)
    """
    use_pyzipper = password is not None

    zf = None
    try:
        if use_pyzipper:
            import pyzipper
            try:
                zf = pyzipper.AESZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel)
                zf.setpassword(password.encode())
                zf.setencryption(pyzipper.WZ_AES, nbits=256)
            except TypeError:
                zf = pyzipper.AESZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED)
                zf.setpassword(password.encode())
                zf.setencryption(pyzipper.WZ_AES, nbits=256)
        else:
            try:
                zf = zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel)
            except TypeError:
                zf = zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED)

        total = len(files)
        done = 0
        with zf:
            for src, rel in files:
                if cancel_event is not None and getattr(cancel_event, 'is_set', lambda: False)():
                    raise RuntimeError('Operation cancelled')
                zf.write(src, arcname=str(rel))
                done += 1
                if verbose:
                    print(f"added {src} as {rel}")
                if progress_callback:
                    try:
                        progress_callback(total, done, src)
                    except Exception:
                        # Progress failures should not stop zipping
                        pass

    except ImportError as e:
        print("Required package missing for encryption: pyzipper", file=sys.stderr)
        raise
