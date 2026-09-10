#!/usr/bin/env python3
"""
Backup the SJ sqlite3 database, ship the backup to a remote host and prune
old backups locally and remotely.

Intended to run from cron every 5 minutes, e.g.:

    */5 * * * * /usr/bin/python3 /app/docker/sqldb-backup.py >> /var/log/sqldb-backup.log 2>&1

Configuration is done via environment variables (with defaults below) so the
script does not need editing when deployed. Remote access relies on SSH
key-based authentication (no passwords are handled by this script).
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --- Configuration (override via environment variables) --------------------
DB_PATH = Path(os.environ.get("SJ_BACKUP_DB_PATH", "/home/sj/projects/data/sj_prd/sj_db_prd.sqlite3"))
LOCAL_BACKUP_DIR = Path(os.environ.get("SJ_BACKUP_LOCAL_DIR", str(DB_PATH.parent / "backups")))
BACKUP_PREFIX = os.environ.get("SJ_BACKUP_PREFIX", "sj_db_prd")

REMOTE_USER = os.environ.get("SJ_BACKUP_REMOTE_USER", "sj")
REMOTE_HOST = os.environ.get("SJ_BACKUP_REMOTE_HOST", "192.168.175.101")
REMOTE_DIR = os.environ.get("SJ_BACKUP_REMOTE_DIR", "/home/sj/projects/data/sj_prd")
REMOTE_LATEST_NAME = os.environ.get("SJ_BACKUP_REMOTE_LATEST_NAME", "sj_db_prd.sqlite3")
REMOTE_SSH_PORT = os.environ.get("SJ_BACKUP_REMOTE_SSH_PORT", "22")
REMOTE_SSH_KEY = os.environ.get("SJ_BACKUP_REMOTE_SSH_KEY", "")  # optional path to a private key

KEEP_BACKUPS = int(os.environ.get("SJ_BACKUP_KEEP", "30"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("sqldb-backup")


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    log.info("Running: %s", " ".join(cmd))
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def create_local_backup() -> Path:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    LOCAL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = LOCAL_BACKUP_DIR / f"{BACKUP_PREFIX}_{timestamp}.sqlite3"

    run(["sqlite3", str(DB_PATH), f".backup '{backup_path}'"])

    # Sanity check: make sure the backup is a valid, readable sqlite3 file.
    check = run(["sqlite3", str(backup_path), "PRAGMA integrity_check;"])
    if check.stdout.strip() != "ok":
        raise RuntimeError(f"Backup integrity check failed: {check.stdout.strip()}")

    log.info("Created local backup: %s", backup_path)
    return backup_path


def ssh_base_args() -> list[str]:
    args = ["ssh", "-p", REMOTE_SSH_PORT]
    if REMOTE_SSH_KEY:
        args += ["-i", REMOTE_SSH_KEY]
    return args


def scp_base_args() -> list[str]:
    args = ["scp", "-P", REMOTE_SSH_PORT]
    if REMOTE_SSH_KEY:
        args += ["-i", REMOTE_SSH_KEY]
    return args


def copy_to_remote(backup_path: Path) -> None:
    if not REMOTE_HOST:
        raise RuntimeError("SJ_BACKUP_REMOTE_HOST is not configured")

    remote_target = f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/"
    run([*ssh_base_args(), f"{REMOTE_USER}@{REMOTE_HOST}", f"mkdir -p '{REMOTE_DIR}'"])
    run([*scp_base_args(), str(backup_path), remote_target])
    log.info("Copied backup to remote host: %s", remote_target)

    # Keep a stable "latest" copy on the remote host, e.g. sj_db_prd.sqlite3
    remote_backup_file = f"{REMOTE_DIR}/{backup_path.name}"
    remote_latest_file = f"{REMOTE_DIR}/{REMOTE_LATEST_NAME}"
    run([*ssh_base_args(), f"{REMOTE_USER}@{REMOTE_HOST}",
         f"cp '{remote_backup_file}' '{remote_latest_file}'"])
    log.info("Updated remote latest copy: %s", remote_latest_file)


def prune_local_backups() -> None:
    backups = sorted(LOCAL_BACKUP_DIR.glob(f"{BACKUP_PREFIX}_*.sqlite3"))
    stale = backups[:-KEEP_BACKUPS] if len(backups) > KEEP_BACKUPS else []
    for old_file in stale:
        old_file.unlink()
        log.info("Removed old local backup: %s", old_file)


def prune_remote_backups() -> None:
    # List, sort and drop everything beyond the last KEEP_BACKUPS files remotely.
    remote_cmd = (
        f"cd '{REMOTE_DIR}' && "
        f"ls -1 {BACKUP_PREFIX}_*.sqlite3 2>/dev/null | sort | head -n -{KEEP_BACKUPS} | "
        f"xargs -r rm -f --"
    )
    run([*ssh_base_args(), f"{REMOTE_USER}@{REMOTE_HOST}", remote_cmd])
    log.info("Pruned remote backups older than the last %d", KEEP_BACKUPS)


def main() -> int:
    try:
        backup_path = create_local_backup()
        copy_to_remote(backup_path)
        prune_local_backups()
        prune_remote_backups()
    except subprocess.CalledProcessError as exc:
        log.error("Command failed (%s): %s", exc.cmd, exc.stderr)
        return 1
    except Exception as exc:
        log.error("Backup failed: %s", exc)
        return 1

    log.info("Backup completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
