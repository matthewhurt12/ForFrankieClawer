#!/usr/bin/env python3
"""
Print the local Frankie skill manifest.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills" / "manifest.json"


def main() -> int:
    if not MANIFEST.exists():
        print(f"Missing manifest: {MANIFEST}")
        return 1

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print("Local Frankie skills")
    print("=" * 80)
    for skill in data.get("skills", []):
        name = skill.get("name", "")
        path = skill.get("path", "")
        summary = skill.get("summary", "")
        slash = ", ".join(skill.get("slash_commands", []))
        triggers = ", ".join(skill.get("triggers", []))
        print(f"\n{name}")
        print(f"  file: {path}")
        if slash:
            print(f"  slash: {slash}")
        if triggers:
            print(f"  triggers: {triggers}")
        if summary:
            print(f"  summary: {summary}")

    print()
    print("Router: COMMANDS.md")
    print("Start here: START_HERE.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
