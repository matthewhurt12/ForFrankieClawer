#!/usr/bin/env python3
"""
First-run orientation helper for Frankie/OpenClaw.

This command is intentionally local-only. It runs the workspace doctor, prints
available skills, and shows the safest next commands without calling paid actors.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(title: str, args: list[str]) -> int:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    proc = subprocess.run(args, cwd=ROOT, text=True)
    return proc.returncode


def print_next_steps() -> None:
    token_status = "set" if os.environ.get("APIFY_TOKEN") else "not set"
    print("\n" + "=" * 80)
    print("Safe next steps")
    print("=" * 80)
    print(f"APIFY_TOKEN: {token_status} (value intentionally hidden)")
    print("")
    print("Read first:")
    print("- START_HERE.md")
    print("- COMMANDS.md")
    print("- FRANKIE_HANDOFF.md")
    print("")
    print("Athens food recommendation:")
    print(r"  python scripts\athens_food.py recommend")
    print(r"  python scripts\athens_food.py random")
    print("")
    print("Local-only arbitrage refresh:")
    print(r"  python scripts\run_arbitrage_pipeline.py")
    print("")
    print("Local-only freebie radar refresh:")
    print(r"  python scripts\freebie_radar.py")
    print("")
    print("SmartCore billing config check:")
    print(r"  python scripts\smartcore_billing.py validate")
    print("")
    print("SmartCore billing preview:")
    print(r"  python scripts\smartcore_billing.py plan --invoice-date YYYY-MM-DD --service-months YYYY-MM --start-number N")
    print("")
    print("Dry run before any paid collection:")
    print(r"  python scripts\run_arbitrage_pipeline.py --dry-run")
    print(r"  python scripts\freebie_radar.py --collect --sources facebook --dry-run")
    print("")
    print("Fresh paid Mercari/Facebook collection, only with Matthew's approval:")
    print(r"  python scripts\run_arbitrage_pipeline.py --collect")
    print("")
    print("Exact-model sold comps only:")
    print(r'  python scripts\run_ebay_sold_comps.py --keywords "Kenwood KR-4600" --clean --merge --refresh-reports')
    print("")
    print("Main reports:")
    print("- reports/DEAL_DESK_REVIEW_001.md")
    print("- reports/PHOTO_VERIFICATION_QUEUE_001.md")
    print("- reports/PIPELINE_RUN_LAST.md")
    print("")
    print("Rules: no BUY verdicts, no fake profit from active listings, no token printing.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    print("Frankie Mind startup")
    print(f"Workspace: {ROOT}")

    doctor_code = run_step("Workspace health check", [sys.executable, "scripts/workspace_doctor.py"])
    skills_code = run_step("Available skills", [sys.executable, "scripts/list_skills.py"])
    pipeline_code = run_step(
        "Arbitrage pipeline dry run",
        [sys.executable, "scripts/run_arbitrage_pipeline.py", "--dry-run"],
    )

    print_next_steps()

    failed = [code for code in (doctor_code, skills_code, pipeline_code) if code != 0]
    if failed:
        print("\nStartup finished with issues. Open reports/WORKSPACE_HEALTH_LAST.md.")
        return 1

    print("\nStartup OK. Frankie can work from the files above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
