#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import getpass

from .core import collect_files, create_zip
from . import __version__


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="zipper", description="Create a zip archive from files and directories")
    p.add_argument('inputs', nargs='+', help='Files or directories to include')
    p.add_argument('-o', '--output', required=True, help='Output zip file path')
    p.add_argument('-l', '--level', type=int, choices=range(0, 10), default=6, help='Compression level 0-9')
    p.add_argument('-r', '--recurse', action='store_true', help='Recurse into directories')
    p.add_argument('-R', '--no-implied-recurse', action='store_true', dest='no_implied_recurse',
                   help='Do not imply recursion for directory inputs (explicit -r required)')
    p.add_argument('-e', '--exclude', action='append', default=[], help='Glob pattern to exclude (can be repeated)')
    p.add_argument('--include-hidden', action='store_true', help='Include hidden files')
    p.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    p.add_argument('-q', '--quiet', action='store_true', help='Quiet mode; suppress progress and non-error output')
    p.add_argument('-f', '--force', action='store_true', help='Overwrite output file if it exists')
    p.add_argument('--encrypt', action='store_true', help='Encrypt archive (AES). You will be prompted for password')
    p.add_argument('--version', action='version', version=__version__)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # If the user didn't explicitly request recursion, but provided one or more
    # directory inputs, assume they want recursion (unless they disabled implied recursion).
    recurse_flag = args.recurse
    if not recurse_flag and not getattr(args, 'no_implied_recurse', False):
        try:
            from pathlib import Path as _Path
            if any(_Path(p).is_dir() for p in args.inputs):
                recurse_flag = True
        except Exception:
            # If anything goes wrong detecting dirs, fall back to provided flag
            pass

    # If output exists and user did not request --force, refuse to overwrite.
    out_path = Path(args.output)
    if out_path.exists() and not getattr(args, 'force', False):
        print(f"Output file already exists: {args.output}. Use --force to overwrite.", file=sys.stderr)
        return 4

    try:
        files = collect_files(args.inputs, recurse_flag, args.exclude, args.include_hidden)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 2

    if not files:
        print("No files to add. Use -r to recurse into directories or check exclude patterns.")
        return 1

    password = None
    if args.encrypt:
        # prompt for password
        pw = getpass.getpass("Enter AES password: ")
        pw2 = getpass.getpass("Confirm password: ")
        if pw != pw2:
            print("Passwords do not match", file=sys.stderr)
            return 3
        password = pw

    # Progress bar: respect --quiet. Try to use tqdm if available.
    progress = None
    if not getattr(args, 'quiet', False):
        try:
            from tqdm import tqdm
            pb = tqdm(total=len(files), unit='file')

            def progress_cb(total, done, current):
                pb.update(1)

            progress = progress_cb
        except Exception:
            progress = None
    else:
        # Quiet: disable verbose output and progress
        args.verbose = False
        progress = None

    create_zip(args.output, files, args.level, args.verbose, password=password, progress_callback=progress)
    try:
        if 'pb' in locals():
            pb.close()
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
