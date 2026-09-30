#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "registry.json"
SCHEMA_PATH = ROOT / "registry" / "schema" / "right-tool-registry.schema.json"


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def duplicate_ids(items, kind: str) -> list[str]:
    counts = Counter(item["id"] for item in items)
    return [f"{kind}: duplicate id {item_id!r}" for item_id, n in counts.items() if n > 1]


def validate_references(registry: dict) -> list[str]:
    errors: list[str] = []

    systems = {item["id"] for item in registry["systems"]}
    triggers = {item["id"] for item in registry["triggers"]}
    evidence = {item["id"] for item in registry["evidence"]}
    experiments = {item["id"] for item in registry["experiments"]}

    for key in ("systems", "triggers", "evidence", "recommendations", "experiments"):
        errors.extend(duplicate_ids(registry[key], key))

    seen_pairs: set[tuple[str, str]] = set()
    for rec in registry["recommendations"]:
        rid = rec["id"]
        trigger_id = rec["trigger_id"]
        system_id = rec["system_id"]

        if trigger_id not in triggers:
            errors.append(f"{rid}: unknown trigger_id {trigger_id!r}")
        if system_id not in systems:
            errors.append(f"{rid}: unknown system_id {system_id!r}")

        pair = (trigger_id, system_id)
        if pair in seen_pairs:
            errors.append(f"{rid}: duplicate trigger/system recommendation pair {pair!r}")
        seen_pairs.add(pair)

        for evidence_id in rec["evidence_ids"]:
            if evidence_id not in evidence:
                errors.append(f"{rid}: unknown evidence_id {evidence_id!r}")

        for experiment_id in rec.get("experiment_ids", []):
            if experiment_id not in experiments:
                errors.append(f"{rid}: unknown experiment_id {experiment_id!r}")

        for alt in rec["closest_alternatives"]:
            alt_id = alt.get("system_id")
            if alt_id is not None and alt_id not in systems:
                errors.append(f"{rid}: unknown closest-alternative system_id {alt_id!r}")

    for experiment in registry["experiments"]:
        for system_id in experiment["system_ids"]:
            if system_id not in systems:
                errors.append(f"{experiment['id']}: unknown system_id {system_id!r}")

    # Enforce the architectural intent: every retained recommendation must
    # include at least one explicit negative discriminator.
    for rec in registry["recommendations"]:
        if not rec["avoid_when"]:
            errors.append(f"{rec['id']}: avoid_when must not be empty")

    return errors


def main() -> int:
    registry = load(REGISTRY_PATH)
    schema = load(SCHEMA_PATH)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = sorted(validator.iter_errors(registry), key=lambda e: list(e.absolute_path))

    if schema_errors:
        print("JSON Schema validation failed:", file=sys.stderr)
        for error in schema_errors:
            path = ".".join(str(part) for part in error.absolute_path) or "<root>"
            print(f"  {path}: {error.message}", file=sys.stderr)
        return 1

    semantic_errors = validate_references(registry)
    if semantic_errors:
        print("Registry integrity validation failed:", file=sys.stderr)
        for error in semantic_errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(
        "registry OK: "
        f"{len(registry['systems'])} systems, "
        f"{len(registry['triggers'])} triggers, "
        f"{len(registry['recommendations'])} recommendations, "
        f"{len(registry['evidence'])} evidence records, "
        f"{len(registry['experiments'])} experiments"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
