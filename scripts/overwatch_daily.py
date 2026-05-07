#!/usr/bin/env python3
"""Frankie wrapper for the real Overwatch WiFi monitor repo."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO = Path(os.environ.get("OVERWATCH_REPO", r"C:\Users\matth\overwatch-wifi-monitor"))


def repo_path() -> Path:
    return DEFAULT_REPO.expanduser()


def print_status(repo: Path) -> int:
    daily = repo / "overwatch_daily.py"
    server = repo / "server.py"
    docs = repo / "docs" / "FRANKIE_OVERWATCH.md"
    db_path = os.environ.get("OVERWATCH_DB", str(repo / "device_registry.db"))
    csv_path = os.environ.get("OVERWATCH_CSV_FILE", "/home/matthew/scan-01.csv")

    print("Overwatch WiFi repo:", repo)
    print("Repo exists:", repo.exists())
    print("Daily script:", daily.exists())
    print("Server:", server.exists())
    print("Frankie guide:", docs.exists())
    print("Configured DB:", db_path)
    print("Configured CSV:", csv_path)
    print()
    print("Daily review:")
    print(r"  python scripts\overwatch_daily.py --no-write --json")
    print("Run server on the Pi:")
    print("  uvicorn server:app --host 0.0.0.0 --port 8001")
    return 0 if repo.exists() and daily.exists() else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?")
    known, rest = parser.parse_known_args(argv)

    repo = repo_path()
    if known.command == "status":
        return print_status(repo)

    daily = repo / "overwatch_daily.py"
    if not daily.exists():
        print(f"Missing Overwatch repo or daily script: {daily}", file=sys.stderr)
        print("Expected repo: https://github.com/matthewhurt12/overwatch-wifi-monitor", file=sys.stderr)
        return 1

    passthrough = argv
    if not passthrough:
        passthrough = ["--no-write"]
    cmd = [sys.executable, str(daily), *passthrough]
    return subprocess.run(cmd, cwd=str(repo), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
