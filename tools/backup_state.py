#!/usr/bin/env python3
"""tools/backup_state.py — simple backup / restore for Samus‑Manus runtime state

Usage:
  python tools/backup_state.py backup            # create timestamped zip in ./backups
  python tools/backup_state.py list              # list available backups
  python tools/backup_state.py restore <file.zip> [--yes]
  python tools/backup_state.py inspect <file.zip>  # show files inside

What it saves by default:
- samus_manus_mvp/heartbeat_state.json
- samus_manus_mvp/tasks.json
- samus_manus_mvp/memory.db
- samus_manus_mvp/approval_audit.log

The script is intentionally conservative: it only copies files that exist and requires explicit --yes to overwrite on restore.
"""
from __future__ import annotations
import argparse
import shutil
import time
from pathlib import Path
import zipfile
import sys

ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT / 'backups'
STATE_DIR = ROOT / 'samus_manus_mvp'
FILES_TO_SAVE = [
    STATE_DIR / 'heartbeat_state.json',
    STATE_DIR / 'tasks.json',
    STATE_DIR / 'memory.db',
    STATE_DIR / 'approval_audit.log',
]


def ensure_backup_dir() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def make_stamp() -> str:
    return time.strftime('%Y%m%dT%H%M%S')


def backup(out: Path | None = None) -> Path:
    ensure_backup_dir()
    ts = make_stamp()
    base = out or (BACKUP_DIR / f'state-{ts}')
    archive_path = Path(shutil.make_archive(str(base), 'zip', root_dir=ROOT, base_dir=None, verbose=False))

    # create a zip containing only the selected files for clarity
    # (overwrite the created zip with a curated one)
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in FILES_TO_SAVE:
            if p.exists():
                zf.write(p, arcname=str(Path('samus_manus_mvp') / p.name))
    print(archive_path)
    return archive_path


def list_backups():
    ensure_backup_dir()
    zips = sorted(BACKUP_DIR.glob('state-*.zip'), reverse=True)
    if not zips:
        print('No backups found in', BACKUP_DIR)
        return
    for z in zips:
        print(z.name)


def inspect(path: Path):
    if not path.exists():
        print('Not found:', path)
        return
    with zipfile.ZipFile(path, 'r') as zf:
        for info in zf.infolist():
            print(f'{info.filename:40}  {info.file_size:8d} bytes')


def restore(path: Path, yes: bool = False):
    if not path.exists():
        print('Backup not found:', path)
        return
    with zipfile.ZipFile(path, 'r') as zf:
        members = zf.namelist()
        print('Will restore the following files:')
        for m in members:
            print('  ', m)
        if not yes:
            ans = input('Proceed and overwrite existing files? (y/N) ').strip().lower()
            if ans not in ('y', 'yes'):
                print('Aborted')
                return
        for m in members:
            target = ROOT / m
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(m) as fr, open(target, 'wb') as fw:
                shutil.copyfileobj(fr, fw)
            print('Restored:', target)
    print('Restore complete.')


def main():
    ap = argparse.ArgumentParser(prog='backup_state', description='Backup/restore Samus‑Manus runtime state')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub_backup = sub.add_parser('backup', help='Create a timestamped backup (zip)')
    sub_backup.add_argument('--out', type=Path, help='Path (without .zip) or zip file to create')

    sub_list = sub.add_parser('list', help='List available backups')

    sub_inspect = sub.add_parser('inspect', help='Show contents of a backup')
    sub_inspect.add_argument('file', type=Path)

    sub_restore = sub.add_parser('restore', help='Restore from a backup zip')
    sub_restore.add_argument('file', type=Path)
    sub_restore.add_argument('--yes', action='store_true', help='Do not prompt before overwrite')

    args = ap.parse_args()
    if args.cmd == 'backup':
        out = args.out
        if out and out.suffix == '.zip':
            out = out.with_suffix('')
        path = backup(out)
        print('Created:', path)
    elif args.cmd == 'list':
        list_backups()
    elif args.cmd == 'inspect':
        inspect(args.file)
    elif args.cmd == 'restore':
        restore(args.file, yes=args.yes)


if __name__ == '__main__':
    main()
