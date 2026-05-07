#!/usr/bin/env python3
"""
One-command arbitrage pipeline for Frankie/OpenClaw.

Default mode is local-only and does not call paid Apify actors. Use --collect
when Matthew explicitly wants a fresh marketplace scrape.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "PIPELINE_RUN_LAST.md"


@dataclass
class StepResult:
    name: str
    command: list[str]
    returncode: int
    output: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run_step(name: str, command: list[str], env: dict[str, str]) -> StepResult:
    print()
    print("=" * 80)
    print(name)
    print("=" * 80)
    print(" ".join(command))
    proc = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout or ""
    print(output)
    return StepResult(name=name, command=command, returncode=proc.returncode, output=output)


def run_parallel_collection(env: dict[str, str], sources: list[str]) -> list[StepResult]:
    commands: list[tuple[str, list[str]]] = []
    if "mercari" in sources:
        commands.append(("Mercari collection", [sys.executable, "scripts/mercari_production_run_001.py"]))
    if "facebook" in sources:
        commands.append(("Facebook Marketplace collection", [sys.executable, "scripts/facebook_marketplace_run_002.py"]))

    print()
    print("=" * 80)
    print("Starting paid Apify collection")
    print("=" * 80)
    print("Sources:", ", ".join(sources))
    print("These scripts use small limits from config/marketplace_sources.json.")

    processes: list[tuple[str, list[str], subprocess.Popen[str]]] = []
    for name, command in commands:
        print(f"Starting: {name}")
        processes.append(
            (
                name,
                command,
                subprocess.Popen(
                    command,
                    cwd=ROOT,
                    env=env,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                ),
            )
        )

    results: list[StepResult] = []
    for name, command, proc in processes:
        output, _ = proc.communicate()
        output = output or ""
        print()
        print("=" * 80)
        print(name)
        print("=" * 80)
        print(output)
        results.append(StepResult(name=name, command=command, returncode=proc.returncode, output=output))

    return results


def write_report(results: list[StepResult], args: argparse.Namespace) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Arbitrage Pipeline Run",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Mode:** {'paid collection + local reports' if args.collect else 'local reports only'}",
        f"**Sources:** {', '.join(args.sources)}",
        "",
        "## Step Results",
        "",
    ]

    for result in results:
        status = "OK" if result.ok else f"FAILED ({result.returncode})"
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"- **Status:** {status}",
                f"- **Command:** `{' '.join(result.command)}`",
                "",
            ]
        )
        tail = "\n".join((result.output or "").splitlines()[-20:])
        if tail:
            lines.extend(["```text", tail, "```", ""])

    lines.extend(
        [
            "## Outputs",
            "",
            f"- Deal Desk: `{rel(ROOT / 'reports' / 'DEAL_DESK_REVIEW_001.md')}`",
            f"- Photo Queue: `{rel(ROOT / 'reports' / 'PHOTO_VERIFICATION_QUEUE_001.md')}`",
            f"- Lead History: `{rel(ROOT / 'reports' / 'LEAD_HISTORY_UPDATE_001.md')}`",
            "",
            "## Rules",
            "",
            "- INVESTIGATE / WATCH / SKIP only.",
            "- No profit estimate without clean sold comps.",
            "- Paid Apify runs require `--collect`.",
            "- eBay sold comps should be run separately with exact model keywords only.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the arbitrage lead pipeline safely.")
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Run paid Apify marketplace actors before local analysis.",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["mercari", "facebook"],
        default=["mercari", "facebook"],
        help="Marketplace sources to collect when --collect is used.",
    )
    parser.add_argument(
        "--skip-history",
        action="store_true",
        help="Skip lead history update.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned steps without running them.",
    )
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    planned: list[tuple[str, list[str]]] = []
    if args.collect:
        if not env.get("APIFY_TOKEN"):
            print("ERROR: APIFY_TOKEN is required for --collect.")
            print("Run local reports without --collect, or set APIFY_TOKEN in the environment.")
            return 2
        for source in args.sources:
            script = "scripts/mercari_production_run_001.py" if source == "mercari" else "scripts/facebook_marketplace_run_002.py"
            planned.append((f"{source.title()} collection", [sys.executable, script]))

    if not args.skip_history:
        planned.append(("Update lead history", [sys.executable, "scripts/update_lead_history.py"]))
    planned.extend(
        [
            ("Generate Deal Desk", [sys.executable, "scripts/deal_desk_review.py"]),
            ("Generate Photo Verification Queue", [sys.executable, "scripts/photo_verification_queue.py"]),
        ]
    )

    if args.dry_run:
        print("Planned steps:")
        for name, command in planned:
            print(f"- {name}: {' '.join(command)}")
        return 0

    results: list[StepResult] = []
    if args.collect:
        results.extend(run_parallel_collection(env, args.sources))
        if not all(result.ok for result in results):
            write_report(results, args)
            print(f"Pipeline stopped after collection failure. Report: {rel(REPORT_PATH)}")
            return 1

    if not args.skip_history:
        results.append(run_step("Update lead history", [sys.executable, "scripts/update_lead_history.py"], env))
    results.append(run_step("Generate Deal Desk", [sys.executable, "scripts/deal_desk_review.py"], env))
    results.append(run_step("Generate Photo Verification Queue", [sys.executable, "scripts/photo_verification_queue.py"], env))

    write_report(results, args)
    print()
    print("=" * 80)
    print("Pipeline complete")
    print("=" * 80)
    print(f"Run report: {rel(REPORT_PATH)}")
    print("Open reports/DEAL_DESK_REVIEW_001.md for recommendations.")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
