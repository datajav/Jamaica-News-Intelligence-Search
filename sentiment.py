import json
from transformers import pipeline

# Load model 

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


# Run 

if __name__ == "__main__":
    # Load articles saved by scraper.py
    with open("articles.json", "r", encoding="utf-8") as f:
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

    # Save enriched results
    with open("articles_with_sentiment.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Quick summary
    from collections import Counter
    counts = Counter(r["label"] for r in results)
    print("─" * 50)
    print(f" Done. Saved to articles_with_sentiment.json")
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