import os
from bertopic import BERTopic
from sklearn.cluster import HDBSCAN
from db import get_untopicked_articles, save_topic, add_topic_column

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    add_topic_column()

    articles = get_untopicked_articles()

    if not articles:
        print("No unassigned articles found. Run scraper.py first.")
        exit()

    print(f"Running BERTopic on {len(articles)} articles...\n")

    docs = [a["headline"] + ". " + a["body"][:500] for a in articles]

    hdbscan_model = HDBSCAN(
        min_cluster_size=2,
        min_samples=1
    )

    topic_model = BERTopic(
        language="english",
        calculate_probabilities=False,
        hdbscan_model=hdbscan_model,
        verbose=True
    )

    topics, _ = topic_model.fit_transform(docs)

    for article, topic_num in zip(articles, topics):
        topic_label = f"topic_{topic_num}"
        save_topic(article["id"], topic_label)
        print(f"  [{topic_label}] {article['headline'][:70]}")

    print(f"\n✅ Topics assigned to {len(articles)} articles.")