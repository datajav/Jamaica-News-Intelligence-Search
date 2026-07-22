import os
import json
from transformers import pipeline
from collections import Counter

# Should resolve paths relative to this script's folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Loads model 

print("Loading sentiment model (first run downloads ~500MB)...")
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512,
)
print("Model loaded.\n")

LABEL_MAP = {
    "positive": "positive",
    "neutral": "neutral",
    "negative": "negative",
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}


def analyze(text):
    """Run sentiment on a piece of text. Returns label + score."""
    result = sentiment_model(text[:512])[0]
    label = LABEL_MAP.get(result["label"].lower(), result["label"].lower())
    return {"label": label, "score": round(result["score"], 4)}


# Run the script.  

if __name__ == "__main__":
    # Load articles saved by scraper.py — always looks in the same folder as this script
    input_file = os.path.join(SCRIPT_DIR, "articles.json")

    if not os.path.exists(input_file):
        print(f"❌ Could not find articles.json at: {input_file}")
        print("   Make sure you ran scraper.py first.")
        exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print(f"Analyzing {len(articles)} articles...\n")

    results = []
    for article in articles:
        # Analyze headline + first 300 chars of body for speed
        text = article["headline"] + ". " + article["body"][:300]
        sentiment = analyze(text)

        enriched = {**article, **sentiment}
        results.append(enriched)

        emoji = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}[sentiment["label"]]
        print(f"{emoji} [{article['source'].upper()}] {sentiment['label'].upper()} ({sentiment['score']})")
        print(f"   {article['headline'][:80]}\n")

    # Save enriched results next to the input file
    output_file = os.path.join(SCRIPT_DIR, "articles_with_sentiment.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Quick summary
    counts = Counter(r["label"] for r in results)
    print("─" * 50)
    print(f"✅ Done. Saved to {output_file}")
    print(f"   🟢 Positive : {counts['positive']}")
    print(f"   🟡 Neutral  : {counts['neutral']}")
    print(f"   🔴 Negative : {counts['negative']}")

    # Per-source breakdown
    print("\nPer-source breakdown:")
    sources = set(r["source"] for r in results)
    for source in sources:
        source_results = [r for r in results if r["source"] == source]
        source_counts = Counter(r["label"] for r in source_results)
        print(f"  {source.upper()}: {dict(source_counts)}")