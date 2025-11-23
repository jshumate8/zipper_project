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


def extract_zip(zip_path, output_dir, password=None, verbose=False, progress_callback=None, cancel_event=None):
    """Extract a zip archive.

    Args:
        zip_path: Path to the zip file
        output_dir: Directory to extract to
        password: Optional password for encrypted zips
        verbose: Print extraction progress
        progress_callback: Optional callable(total, done, current_path)
        cancel_event: Optional threading.Event to cancel extraction
    """
    zip_path = Path(zip_path)
    output_dir = Path(output_dir)
    
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Try pyzipper first for AES support, fall back to zipfile
    try:
        if password:
            import pyzipper
            zf = pyzipper.AESZipFile(zip_path, 'r')
            if password:
                zf.setpassword(password.encode())
        else:
            zf = zipfile.ZipFile(zip_path, 'r')
    except ImportError:
        # No pyzipper, use standard zipfile
        zf = zipfile.ZipFile(zip_path, 'r')
        if password:
            zf.setpassword(password.encode())
    
    with zf:
        members = zf.namelist()
        total = len(members)
        done = 0
        
        for member in members:
            if cancel_event is not None and getattr(cancel_event, 'is_set', lambda: False)():
                raise RuntimeError('Operation cancelled')
            
            zf.extract(member, output_dir)
            done += 1
            
            if verbose:
                print(f"extracted {member}")
            
            if progress_callback:
                try:
                    progress_callback(total, done, member)
                except Exception:
                    pass
    
    return output_dir
