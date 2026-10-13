#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "registry.json"


def parse_day(value: str) -> date:
    return date.fromisoformat(value)


def audit(registry: dict, today: date) -> dict:
    evidence = {e["id"]: e for e in registry["evidence"]}
    errors: list[str] = []
    warnings: list[str] = []
    stale: list[dict] = []

    for item in registry["evidence"]:
        checked = parse_day(item["last_checked_on"])
        age = (today - checked).days
        limit = int(item["review_after_days"])
        if item["status"] == "current" and age > limit:
            stale.append(
                {
                    "evidence_id": item["id"],
                    "last_checked_on": item["last_checked_on"],
                    "age_days": age,
                    "review_after_days": limit,
                }
            )
        if item["status"] == "superseded" and not item.get("superseded_by"):
            warnings.append(f"{item['id']}: superseded evidence has no superseded_by link")

    for rec in registry["recommendations"]:
        linked = []
        for evidence_id in rec["evidence_ids"]:
            item = evidence.get(evidence_id)
            if item is None:
                errors.append(f"{rec['id']}: missing evidence {evidence_id!r}")
            else:
                linked.append(item)

        if rec["status"] in {"current", "provisional"} and not linked:
            errors.append(f"{rec['id']}: active recommendation has no evidence")

        if linked and rec["status"] in {"current", "provisional"}:
            if all(e["status"] == "superseded" for e in linked):
                errors.append(f"{rec['id']}: all linked evidence is superseded")
            if any(e["status"] == "disputed" for e in linked) and rec["status"] == "current":
                warnings.append(
                    f"{rec['id']}: current recommendation depends on disputed evidence"
                )

    return {
        "today": today.isoformat(),
        "counts": {
            "evidence": len(registry["evidence"]),
            "recommendations": len(registry["recommendations"]),
            "stale": len(stale),
            "warnings": len(warnings),
            "errors": len(errors),
        },
        "stale": stale,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit right-tool claim/evidence lifecycle.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict-stale",
        action="store_true",
        help="fail when current evidence is past its review_after_days window",
    )
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    result = audit(registry, date.today())

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        c = result["counts"]
        print(
            f"evidence audit: {c['evidence']} evidence records, "
            f"{c['recommendations']} recommendations, "
            f"{c['stale']} stale, {c['warnings']} warnings, {c['errors']} errors"
        )
        for message in result["warnings"]:
            print(f"warning: {message}")
        for item in result["stale"]:
            print(
                "stale: "
                f"{item['evidence_id']} last checked {item['last_checked_on']} "
                f"({item['age_days']}d > {item['review_after_days']}d)"
            )
        for message in result["errors"]:
            print(f"error: {message}")

    if result["errors"]:
        return 1
    if args.strict_stale and result["stale"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
