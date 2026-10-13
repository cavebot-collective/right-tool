from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

STRENGTH_RANK = {
    "candidate": 1,
    "strong": 2,
    "very-strong": 3,
    "extremely-strong": 4,
}

STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","i","in","into","is","it",
    "my","of","on","or","that","the","this","to","with","without","am","need","want",
    "writing","write","building","build","some","something","just","where","when",
}

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[+#][a-z0-9+#]*)?", re.IGNORECASE)


def _registry_candidates() -> Iterable[Path]:
    env = os.environ.get("RIGHT_TOOL_REGISTRY")
    if env:
        yield Path(env)
    here = Path(__file__).resolve()
    yield here.parents[1] / "registry" / "registry.json"
    yield here.parent / "data" / "registry.json"


def load_registry(path: str | os.PathLike[str] | None = None) -> dict:
    candidates = [Path(path)] if path else list(_registry_candidates())
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as f:
                return json.load(f)
    tried = "\n  ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"right-tool registry not found; tried:\n  {tried}")


def normalize(text: str) -> str:
    return " ".join(TOKEN_RE.findall(text.lower()))


def tokens(text: str) -> set[str]:
    out = set()
    for token in TOKEN_RE.findall(text.lower()):
        if token not in STOPWORDS and (len(token) > 1 or token in {"r"}):
            out.add(token)
    return out


def _trigger_score(trigger: dict, query: str) -> tuple[int, list[str]]:
    q_norm = normalize(query)
    q_tokens = tokens(query)
    score = 0
    reasons: list[str] = []

    family = trigger["family"].replace("-", " ")
    if family in q_norm:
        score += 6
        reasons.append(f"family:{trigger['family']}")

    keyword_tokens: set[str] = set()
    for keyword in trigger.get("keywords", []):
        k_norm = normalize(keyword)
        k_tokens = tokens(keyword)
        keyword_tokens |= k_tokens
        if k_norm and k_norm in q_norm:
            score += 10
            reasons.append(f"keyword:{keyword}")

    smell_tokens = tokens(trigger["smell"])
    desc_tokens = tokens(trigger["description"])
    signal_tokens = set()
    for signal in trigger.get("positive_signals", []):
        signal_tokens |= tokens(signal)

    kw_overlap = q_tokens & keyword_tokens
    smell_overlap = q_tokens & smell_tokens
    signal_overlap = q_tokens & signal_tokens
    desc_overlap = q_tokens & desc_tokens

    score += 5 * len(kw_overlap)
    score += 3 * len(smell_overlap)
    score += 2 * len(signal_overlap)
    score += 1 * len(desc_overlap)

    for label, overlap in (
        ("keyword-token", kw_overlap),
        ("smell-token", smell_overlap),
        ("signal-token", signal_overlap),
        ("description-token", desc_overlap),
    ):
        for token in sorted(overlap):
            reasons.append(f"{label}:{token}")

    return score, reasons


def find_matches(registry: dict, query: str, limit: int = 5) -> list[dict]:
    systems = {s["id"]: s for s in registry["systems"]}
    recs_by_trigger: dict[str, list[dict]] = {}
    for rec in registry["recommendations"]:
        recs_by_trigger.setdefault(rec["trigger_id"], []).append(rec)

    matches: list[dict] = []
    for trigger in registry["triggers"]:
        score, reasons = _trigger_score(trigger, query)
        if score <= 0:
            continue

        recs = sorted(
            recs_by_trigger.get(trigger["id"], []),
            key=lambda r: (-STRENGTH_RANK.get(r["strength"], 0), r["system_id"]),
        )
        recommendations = []
        for rec in recs:
            system = systems[rec["system_id"]]
            recommendations.append(
                {
                    "system": {
                        "id": system["id"],
                        "name": system["name"],
                        "category": system["category"],
                    },
                    "strength": rec["strength"],
                    "advantage": rec["advantage"],
                    "avoid_when": rec["avoid_when"],
                    "boundary": rec["boundary"],
                    "crossing_cost": rec["crossing_cost"],
                    "confidence": rec["confidence"],
                    "example": rec["example"],
                }
            )

        matches.append(
            {
                "score": score,
                "matched_by": reasons,
                "trigger": {
                    "id": trigger["id"],
                    "family": trigger["family"],
                    "smell": trigger["smell"],
                    "description": trigger["description"],
                    "positive_signals": trigger.get("positive_signals", []),
                    "negative_signals": trigger.get("negative_signals", []),
                },
                "recommendations": recommendations,
            }
        )

    matches.sort(
        key=lambda m: (
            -m["score"],
            -max(
                (STRENGTH_RANK.get(r["strength"], 0) for r in m["recommendations"]),
                default=0,
            ),
            m["trigger"]["id"],
        )
    )
    return matches[: max(limit, 0)]


def resolve_system(registry: dict, query: str) -> dict | None:
    needle = query.strip().lower()
    exact: list[dict] = []
    partial: list[dict] = []

    for system in registry["systems"]:
        names = [system["id"], system["name"], *system.get("aliases", [])]
        lowered = [n.lower() for n in names]
        if needle in lowered:
            exact.append(system)
        elif any(needle in n for n in lowered):
            partial.append(system)

    if len(exact) == 1:
        return exact[0]
    if not exact and len(partial) == 1:
        return partial[0]
    return None


def system_details(registry: dict, system: dict) -> dict:
    triggers = {t["id"]: t for t in registry["triggers"]}
    uses = []
    for rec in registry["recommendations"]:
        if rec["system_id"] != system["id"]:
            continue
        trigger = triggers[rec["trigger_id"]]
        uses.append(
            {
                "trigger": {
                    "id": trigger["id"],
                    "family": trigger["family"],
                    "smell": trigger["smell"],
                },
                "strength": rec["strength"],
                "advantage": rec["advantage"],
                "avoid_when": rec["avoid_when"],
                "boundary": rec["boundary"],
                "crossing_cost": rec["crossing_cost"],
                "confidence": rec["confidence"],
                "example": rec["example"],
            }
        )
    uses.sort(key=lambda x: (x["trigger"]["family"], x["trigger"]["id"]))
    return {"system": system, "recommendations": uses}


def _render_find(query: str, matches: list[dict]) -> str:
    if not matches:
        return f"No registry trigger matched: {query!r}"
    lines = [f"right-tool matches for: {query}", ""]
    for i, match in enumerate(matches, 1):
        t = match["trigger"]
        lines.append(f"{i}. [{match['score']}] {t['smell']}  ({t['family']})")
        for rec in match["recommendations"]:
            s = rec["system"]
            lines.append(
                f"   -> {s['name']} [{rec['strength']}] via {rec['boundary']['kind']}"
            )
            lines.append(f"      why: {rec['advantage']}")
            lines.append(f"      boundary: {rec['boundary']['interface']}")
            lines.append(f"      avoid: {'; '.join(rec['avoid_when'])}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_show(details: dict) -> str:
    s = details["system"]
    lines = [
        f"{s['name']} ({s['id']})",
        f"category: {s['category']}",
        f"description: {s['description']}",
        f"maturity: {s['maturity']['status']} as of {s['maturity']['observed_on']}",
        f"license: {s['licensing']['model']}",
    ]
    if s.get("homepage"):
        lines.append(f"homepage: {s['homepage']}")
    lines.append("")
    for rec in details["recommendations"]:
        t = rec["trigger"]
        lines.append(f"- {t['smell']}  ({t['family']})")
        lines.append(f"  strength: {rec['strength']}")
        lines.append(f"  why: {rec['advantage']}")
        lines.append(f"  boundary: {rec['boundary']['kind']} — {rec['boundary']['interface']}")
        lines.append(f"  avoid: {'; '.join(rec['avoid_when'])}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="right-tool",
        description="Find specialist systems worth crossing an ecosystem boundary for.",
    )
    parser.add_argument(
        "--registry",
        help="override registry path (also supported via RIGHT_TOOL_REGISTRY)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    find = sub.add_parser("find", help="match a prose problem/smell against registry triggers")
    find.add_argument("query", nargs="+")
    find.add_argument("--limit", type=int, default=5)
    find.add_argument("--json", action="store_true")

    show = sub.add_parser("show", help="show one system and the triggers that lead to it")
    show.add_argument("system")
    show.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = load_registry(args.registry)

    if args.command == "find":
        query = " ".join(args.query)
        matches = find_matches(registry, query, args.limit)
        if args.json:
            print(json.dumps({"query": query, "matches": matches}, indent=2, ensure_ascii=False))
        else:
            print(_render_find(query, matches))
        return 0 if matches else 1

    if args.command == "show":
        system = resolve_system(registry, args.system)
        if system is None:
            print(f"No unique system match for {args.system!r}", file=sys.stderr)
            return 2
        details = system_details(registry, system)
        if args.json:
            print(json.dumps(details, indent=2, ensure_ascii=False))
        else:
            print(_render_show(details))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
