from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
MARKER = "RIGHT_TOOL_TIKA_MARKER_271828"
FILES = sorted(FIX.iterdir())

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name: str):
    return importlib.import_module(name)

def timed(module_name: str, dest: Path):
    mod = load(module_name)
    dest.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rows = []
    for path in FILES:
        error = None
        text = ""
        try:
            text = mod.extract(path)
            success = MARKER in text
        except Exception as exc:
            success = False
            error = repr(exc)
        (dest / f"{path.name}.txt").write_text(text, encoding="utf-8")
        rows.append(
            {
                "file": path.name,
                "success": success,
                "error": error,
                "output_chars": len(text),
            }
        )
    return time.perf_counter() - started, rows

def source_metrics(path: Path):
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = [
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    branches = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            src = ast.get_source_segment(text, node.test) or ""
            if "ext" in src or "suffix" in src:
                branches += 1
    return {
        "noncomment_source_lines": len(lines),
        "format_dispatch_branches": branches,
    }

def package_versions():
    names = [
        "beautifulsoup4",
        "openpyxl",
        "pypdf",
        "python-docx",
        "python-pptx",
        "reportlab",
        "striprtf",
    ]
    out = {}
    for name in names:
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = None
    return out

jar = Path(os.environ["TIKA_JAR"])
tika_version = subprocess.check_output(
    ["java", "-jar", str(jar), "--version"], text=True
).strip()

results = {
    "schema_version": 1,
    "files": [
        {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in FILES
    ],
    "versions": {
        "python": sys.version.split()[0],
        "java": subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT, text=True
        ).splitlines()[0],
        "platform": platform.platform(),
        "tika": tika_version,
        "tika_jar_sha256": sha256(jar),
        "python_packages": package_versions(),
    },
}

for name in ["tika_extractor", "python_extractor"]:
    cold, cold_rows = timed(name, OUT / name.replace("_extractor", ""))
    second, second_rows = timed(name, OUT / name.replace("_extractor", ""))
    src = ROOT / f"{name}.py"
    results[name.replace("_extractor", "")] = {
        "cold_seconds": cold,
        "second_seconds": second,
        "cold": cold_rows,
        "second": second_rows,
        "coverage": sum(row["success"] for row in second_rows),
        "source_metrics": source_metrics(src),
    }

(ROOT / "results.json").write_text(
    json.dumps(results, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(results, indent=2))
