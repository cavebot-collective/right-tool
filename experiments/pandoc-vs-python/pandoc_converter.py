from pathlib import Path
import subprocess

def convert(path: Path) -> str:
    cp = subprocess.run(
        ['pandoc', str(path), '-t', 'gfm', '--wrap=none'],
        check=True, capture_output=True, text=True,
    )
    return cp.stdout
