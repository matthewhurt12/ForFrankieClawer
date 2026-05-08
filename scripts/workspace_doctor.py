#!/usr/bin/env python3
"""
Workspace health check for Frankie Mind.

This does not call external services. It validates navigation files, skill
manifests, active scripts, and common safety guardrails.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "WORKSPACE_HEALTH_LAST.md"


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


REQUIRED_FILES = [
    "START_HERE.md",
    "COMMANDS.md",
    "AGENTS.md",
    "TOOLS.md",
    "MEMORY.md",
    "FRANKIE_HANDOFF.md",
    "skills/README.md",
    "skills/manifest.json",
    ".openclaw/skill-manifest.json",
    "skills/intent-router/SKILL.md",
    "skills/voice-output/SKILL.md",
    "scripts/frankie_start.py",
    "scripts/list_skills.py",
    "scripts/intent_router.py",
    "scripts/athens_food.py",
    "scripts/athens_food_google_check.py",
    "scripts/athens_food_go_now.py",
    "scripts/refresh_athens_restaurants.py",
    "scripts/test_athens_food_filters.py",
    "scripts/smartcore_billing.py",
    "scripts/freebie_radar.py",
    "scripts/run_arbitrage_pipeline.py",
    "scripts/run_ebay_sold_comps.py",
    "config/apify_actor_catalog.json",
    "config/freebie_radar.json",
    "config/smartcore_billing.json",
    "data/restaurants/athens_restaurants.csv",
    "data/voice_outputs/README.md",
    "reports/OPENCLAW_ARBITRAGE_RUNBOOK.md",
    "docs/APIFY_ACTOR_CATALOG.md",
    "docs/ATHENS_FOOD_SKILL.md",
    "docs/ATHENS_FOOD_ROADMAP.md",
    "docs/VOICE_OUTPUT.md",
    "docs/FREEBIE_RADAR.md",
    "docs/SMARTCORE_BILLING_SYSTEM.md",
]

ACTIVE_PYTHON = [
    "scripts/frankie_start.py",
    "scripts/list_skills.py",
    "scripts/intent_router.py",
    "scripts/athens_food.py",
    "scripts/athens_food_google_check.py",
    "scripts/athens_food_go_now.py",
    "scripts/refresh_athens_restaurants.py",
    "scripts/test_athens_food_filters.py",
    "scripts/smartcore_billing.py",
    "scripts/freebie_radar.py",
    "scripts/run_arbitrage_pipeline.py",
    "scripts/run_ebay_sold_comps.py",
    "scripts/arbitrage_logic.py",
    "scripts/deal_desk_review.py",
    "scripts/photo_verification_queue.py",
    "scripts/clean_ebay_sold_comps.py",
    "scripts/update_lead_history.py",
]

SECRET_PATTERNS = [
    re.compile(r"apify_api_[A-Za-z0-9_-]+"),
    re.compile(r"sk-ant-api[0-9A-Za-z_-]+"),
    re.compile(r"sk-proj-[0-9A-Za-z_-]+"),
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_required_files() -> list[Check]:
    checks: list[Check] = []
    for item in REQUIRED_FILES:
        path = ROOT / item
        checks.append(Check(f"required file: {item}", path.exists(), "present" if path.exists() else "missing"))
    return checks


def load_json(path: Path) -> tuple[dict, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), "ok"
    except Exception as exc:
        return {}, str(exc)


def check_skill_manifest() -> list[Check]:
    checks: list[Check] = []
    manifest_path = ROOT / "skills" / "manifest.json"
    data, error = load_json(manifest_path)
    if error != "ok":
        return [Check("skills manifest parses", False, error)]

    checks.append(Check("skills manifest parses", True, "ok"))
    names = set()
    for skill in data.get("skills", []):
        name = skill.get("name", "")
        path = ROOT / skill.get("path", "")
        names.add(name)
        checks.append(Check(f"skill path: {name}", path.exists(), rel(path) if path.exists() else f"missing {path}"))

    expected = {
        "intent-router",
        "arbitrage-deal-desk",
        "athens-food",
        "voice-output",
        "freebie-radar",
        "smartcore-billing",
        "apify-actors",
        "overwatch-rf",
        "page-map",
        "signals",
        "radar",
        "bigpic",
        "ideas",
    }
    missing = sorted(expected - names)
    checks.append(Check("expected skills listed", not missing, "ok" if not missing else f"missing: {', '.join(missing)}"))
    return checks


def check_openclaw_manifest() -> Check:
    data, error = load_json(ROOT / ".openclaw" / "skill-manifest.json")
    if error != "ok":
        return Check("openclaw manifest parses", False, error)
    return Check("openclaw manifest parses", bool(data.get("skills")), f"{len(data.get('skills', []))} skills")


def check_python_compile() -> Check:
    files = [str(ROOT / path) for path in ACTIVE_PYTHON if (ROOT / path).exists()]
    if not files:
        return Check("active python compile", False, "no active python files found")
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", *files],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return Check("active python compile", proc.returncode == 0, (proc.stdout or "ok").strip() or "ok")


def check_gitignore() -> list[Check]:
    path = ROOT / ".gitignore"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_patterns = [
        ".env",
        "*.token",
        "credentials/",
        "data/external_leads/*.json",
        "data/ebay_active_search/*.json",
        "data/sold_comps/*.json",
        "data/sold_comps/*_clean.csv",
        "data/freebie_radar/raw/",
        "data/restaurants/enrichment/*.json",
        "data/voice_outputs/*",
        "data/smartcore_billing/generated/",
        "data/browser_test_*/",
        "screenshots/browser_test_*/",
    ]
    return [
        Check(f"gitignore pattern: {pattern}", pattern in text, "present" if pattern in text else "missing")
        for pattern in required_patterns
    ]


def check_secret_strings() -> Check:
    hits: list[str] = []
    ignored_dirs = {".git", "__pycache__", "node_modules"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            hits.append(rel(path))
    return Check("secret token scan", not hits, "ok" if not hits else f"possible tokens in: {', '.join(sorted(set(hits)))}")


def write_report(checks: list[Check]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    failed = [check for check in checks if not check.ok]
    lines = [
        "# Workspace Health",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Status:** {'OK' if not failed else 'NEEDS_ATTENTION'}",
        "",
        "## Summary",
        "",
        f"- **Checks:** {len(checks)}",
        f"- **Passed:** {len(checks) - len(failed)}",
        f"- **Failed:** {len(failed)}",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        mark = "OK" if check.ok else "FAIL"
        lines.append(f"- **{mark}:** {check.name} - {check.detail}")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    checks: list[Check] = []
    checks.extend(check_required_files())
    checks.extend(check_skill_manifest())
    checks.append(check_openclaw_manifest())
    checks.append(check_python_compile())
    checks.extend(check_gitignore())
    checks.append(check_secret_strings())

    write_report(checks)
    failed = [check for check in checks if not check.ok]
    for check in checks:
        mark = "OK" if check.ok else "FAIL"
        print(f"{mark}: {check.name} - {check.detail}")
    print(f"Report written: {rel(REPORT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
