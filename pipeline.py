import subprocess
import sys
from datetime import datetime

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
    print(f"{'─' * 50}")
    result = subprocess.run([PYTHON, script], capture_output=False)
    if result.returncode != 0:
        print(f"✗ {label} failed with exit code {result.returncode}")
        return False
    print(f"✓ {label} complete")
    return True

if __name__ == "__main__":
    print(f"🗞  Jamaica News Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    for label, script in STEPS:
        success = run_step(label, script)
        if not success:
            print(f"\n⚠️  Pipeline stopped at {label}. Fix the error and re-run.")
            sys.exit(1)

    print(f"\n{'═' * 50}")
    print(f"✅ Pipeline complete — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'═' * 50}")