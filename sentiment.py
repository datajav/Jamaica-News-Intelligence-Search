import os
from transformers import pipeline
from collections import Counter
from db import get_unscored_articles, save_sentiment

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
    articles = get_unscored_articles()

    if not articles:
        print("No unscored articles found. Run scraper.py first.")
        exit()

    print(f"Analyzing {len(articles)} articles...\n")

    for article in articles:
        text = article["headline"] + ". " + article["body"][:300]
        sentiment = analyze(text)

        save_sentiment(article["id"], sentiment["label"], sentiment["score"])

        emoji = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}[sentiment["label"]]
        print(f"{emoji} [{article['source'].upper()}] {sentiment['label'].upper()} ({sentiment['score']})")
        print(f"   {article['headline'][:80]}\n")

    print("─" * 50)
    print("✅ Sentiment scoring complete.")