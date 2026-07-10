"""Restart helpers for local Streamlit development."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def clear_pycache(root: Path | None = None) -> int:
    base = root or PROJECT_ROOT
    removed = 0
    for cache_dir in base.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
            removed += 1
    return removed


def kill_port(port: int) -> list[int]:
    """Terminate processes listening on a TCP port (Windows). Returns killed PIDs."""
    killed: list[int] = []
    if os.name != "nt":
        return killed

    try:
        output = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return killed

    for line in output.splitlines():
        if f":{port}" not in line or "LISTENING" not in line.upper():
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            pid = int(parts[-1])
        except ValueError:
            continue
        if pid <= 0 or pid in killed:
            continue
        result = subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            killed.append(pid)
    return killed


def prepare_fresh_start(port: int = 8501) -> None:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    clear_pycache()
    kill_port(port)


def main(argv: list[str] | None = None) -> int:
    port = 8501
    if argv and argv[0].isdigit():
        port = int(argv[0])
    killed = kill_port(port)
    removed = clear_pycache()
    print(f"Cleared {removed} __pycache__ folder(s)")
    if killed:
        print(f"Stopped process(es) on port {port}: {', '.join(map(str, killed))}")
    else:
        print(f"No listener found on port {port}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
