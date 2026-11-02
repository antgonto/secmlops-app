"""Lineage helpers — no shell, no injection surface."""
import hashlib
import subprocess


def git_sha(short: bool = False) -> str:
    args = ["git", "rev-parse", "--short", "HEAD"] if short else ["git", "rev-parse", "HEAD"]
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
