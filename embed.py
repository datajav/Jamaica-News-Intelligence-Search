import os
import numpy as np
from sentence_transformers import SentenceTransformer
from db import get_unembedded_articles, save_embedding, init_db

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "all-MiniLM-L6-v2"

if __name__ == "__main__":
    init_db()

    articles = get_unembedded_articles()

    if not articles:
        print("All articles already embedded.")
        exit()

    print(f"Embedding {len(articles)} articles...")
    model = SentenceTransformer(MODEL_NAME)

    for article in articles:
        text = article["headline"] + ". " + article["body"][:500]
        vector = model.encode(text)
        save_embedding(article["id"], vector.tobytes())
        print(f"  ✓ {article['headline'][:70]}")

    print(f"\n✅ Done — {len(articles)} articles embedded.")