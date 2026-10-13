#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "registry.json"
MMD_PATH = ROOT / "docs" / "triage.mmd"
MD_PATH = ROOT / "docs" / "triage.md"


def load_registry() -> dict:
    with REGISTRY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def node_id(prefix: str, raw: str) -> str:
    return prefix + re.sub(r"[^A-Za-z0-9_]", "_", raw)


def compact(text: str) -> str:
    return " ".join(text.split())


def clip(text: str, limit: int) -> str:
    text = compact(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def mermaid_text(text: str) -> str:
    text = html.escape(text, quote=False)
    return text.replace('"', "'")


def md_cell(text: str) -> str:
    return compact(text).replace("|", "\\|")


def family_title(family: str) -> str:
    return family.replace("-", " ").title()


def generate_mermaid(registry: dict) -> str:
    systems = {item["id"]: item for item in registry["systems"]}
    triggers = {item["id"]: item for item in registry["triggers"]}
    recs_by_trigger: dict[str, list[dict]] = defaultdict(list)
    for rec in registry["recommendations"]:
        recs_by_trigger[rec["trigger_id"]].append(rec)

    lines = [
        "flowchart LR",
        '  root(["What kind of machinery are you about to reinvent?"])',
    ]

    families = sorted({trigger["family"] for trigger in registry["triggers"]})
    for family in families:
        fid = node_id("family_", family)
        lines.append(f'  {fid}["{mermaid_text(family_title(family))}"]')
        lines.append(f"  root --> {fid}")

    system_nodes: set[str] = set()

    for trigger in sorted(registry["triggers"], key=lambda t: (t["family"], t["id"])):
        tid = node_id("trigger_", trigger["id"])
        fid = node_id("family_", trigger["family"])
        smell = mermaid_text(clip(trigger["smell"], 95))
        lines.append(f'  {tid}["{smell}"]')
        lines.append(f"  {fid} --> {tid}")

        for rec in sorted(recs_by_trigger.get(trigger["id"], []), key=lambda r: r["system_id"]):
            system = systems[rec["system_id"]]
            gid = node_id("guide_", rec["id"])
            sid = node_id("system_", system["id"])
            why = mermaid_text(clip(rec["advantage"], 105))
            avoid = mermaid_text(clip(rec["avoid_when"][0], 80))
            boundary = mermaid_text(rec["boundary"]["kind"])
            strength = mermaid_text(rec["strength"])
            name = mermaid_text(system["name"])
            lines.append(
                f'  {gid}["{name}<br/>'
                f'{strength} · {boundary}<br/>'
                f'Why: {why}<br/>'
                f'Avoid if: {avoid}"]'
            )
            lines.append(f"  {tid} --> {gid}")
            if sid not in system_nodes:
                category = mermaid_text(system["category"])
                lines.append(f'  {sid}(["{name}<br/>{category}"])')
                system_nodes.add(sid)
            lines.append(f"  {gid} --> {sid}")

    lines.extend(
        [
            "",
            "  classDef root fill:#111827,color:#ffffff,stroke:#111827,stroke-width:2px;",
            "  classDef family fill:#e0f2fe,color:#0c4a6e,stroke:#0284c7,stroke-width:1px;",
            "  classDef trigger fill:#f8fafc,color:#0f172a,stroke:#64748b,stroke-width:1px;",
            "  classDef guide fill:#fef3c7,color:#78350f,stroke:#d97706,stroke-width:1px;",
            "  classDef system fill:#dcfce7,color:#14532d,stroke:#16a34a,stroke-width:2px;",
            "  class root root;",
        ]
    )

    family_ids = ",".join(node_id("family_", family) for family in families)
    trigger_ids = ",".join(node_id("trigger_", t["id"]) for t in registry["triggers"])
    guide_ids = ",".join(node_id("guide_", r["id"]) for r in registry["recommendations"])
    system_ids = ",".join(sorted(system_nodes))

    if family_ids:
        lines.append(f"  class {family_ids} family;")
    if trigger_ids:
        lines.append(f"  class {trigger_ids} trigger;")
    if guide_ids:
        lines.append(f"  class {guide_ids} guide;")
    if system_ids:
        lines.append(f"  class {system_ids} system;")

    return "\n".join(lines) + "\n"


def generate_markdown(registry: dict, mermaid: str) -> str:
    systems = {item["id"]: item for item in registry["systems"]}
    triggers = {item["id"]: item for item in registry["triggers"]}

    rows = []
    for rec in sorted(
        registry["recommendations"],
        key=lambda r: (
            triggers[r["trigger_id"]]["family"],
            triggers[r["trigger_id"]]["smell"],
            systems[r["system_id"]]["name"],
        ),
    ):
        trigger = triggers[rec["trigger_id"]]
        system = systems[rec["system_id"]]
        rows.append(
            "| "
            + " | ".join(
                [
                    md_cell(family_title(trigger["family"])),
                    md_cell(trigger["smell"]),
                    md_cell(system["name"]),
                    md_cell(rec["advantage"]),
                    md_cell("; ".join(rec["avoid_when"])),
                    md_cell(rec["boundary"]["kind"] + " — " + rec["boundary"]["interface"]),
                ]
            )
            + " |"
        )

    parts = [
        "# Subsystem triage atlas",
        "",
        "> Generated from `registry/registry.json` by `scripts/generate_triage.py`. Do not edit generated sections by hand.",
        "",
        "Start with the implementation smell you recognize, then follow the branch toward a specialist candidate. The amber guidance node explains why the crossing may pay and the first strong reason not to cross. Green system nodes are shared terminals, so multiple smells can converge on one specialist.",
        "",
        "## Decision DAG",
        "",
        "```mermaid",
        mermaid.rstrip(),
        "```",
        "",
        "## Readable decision table",
        "",
        "| Family | Implementation smell | Candidate | Why consider it | Avoid when | Cheapest boundary |",
        "| --- | --- | --- | --- | --- | --- |",
        *rows,
        "",
        "## Design constraints",
        "",
        "- This is a DAG, not a forced tree: shared terminal systems preserve convergence.",
        "- Guidance is recommendation-edge data, not duplicated system metadata.",
        "- Every recommendation has explicit negative discrimination through `avoid_when`.",
        "- The diagram and table are generated from the same canonical registry consumed by the future CLI.",
        "",
    ]
    return "\n".join(parts)


def main() -> int:
    registry = load_registry()
    mermaid = generate_mermaid(registry)
    markdown = generate_markdown(registry, mermaid)

    MMD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MMD_PATH.write_text(mermaid, encoding="utf-8")
    MD_PATH.write_text(markdown, encoding="utf-8")
    print(
        f"generated {MMD_PATH.relative_to(ROOT)} and {MD_PATH.relative_to(ROOT)} "
        f"from {len(registry['triggers'])} triggers / {len(registry['recommendations'])} recommendations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
