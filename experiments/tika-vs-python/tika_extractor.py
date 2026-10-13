from __future__ import annotations

import os
import subprocess
from pathlib import Path

JAR = os.environ["TIKA_JAR"]

def extract(path: Path) -> str:
    cp = subprocess.run(
        ["java", "-jar", JAR, "--text", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return cp.stdout
