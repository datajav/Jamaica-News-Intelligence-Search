import os
import subprocess
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

STEPS = [
    ("Scraper",    "scraper.py"),
    ("Sentiment",  "sentiment.py"),
    ("Topics",     "topics.py"),
    ("Embeddings", "embed.py"),
]

def run_step(label, script):
    print(f"\n{'─' * 50}")
    print(f"▶ {label} — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'─' * 50}", flush=True)
    result = subprocess.run(
    [PYTHON, os.path.join(SCRIPT_DIR, script)],
    cwd=SCRIPT_DIR,
    env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode != 0:
        print(f"✗ {label} failed with exit code {result.returncode}")
        return False
    print(f"✓ {label} complete")
    return True

if __name__ == "__main__":
    print(f"Jamaica News Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    for label, script in STEPS:
        if not run_step(label, script):
            print(f"\nPipeline stopped at {label}.")
            sys.exit(1)

    print(f"\nPipeline complete — {datetime.now().strftime('%H:%M:%S')}")