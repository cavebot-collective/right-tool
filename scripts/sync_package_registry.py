#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "registry" / "registry.json"
TARGET = ROOT / "right_tool" / "data" / "registry.json"

TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
print(f"synced {SOURCE.relative_to(ROOT)} -> {TARGET.relative_to(ROOT)}")
