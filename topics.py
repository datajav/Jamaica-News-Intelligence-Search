import os
from bertopic import BERTopic
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from db import get_untopicked_articles, save_topic, add_topic_column

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_topic_labels(topic_model):
    """Build human-readable labels from top keywords per topic."""
    labels = {}
    for topic_num in topic_model.get_topics():
        if topic_num == -1:
            labels[topic_num] = "outlier"
            continue
        words = [word for word, _ in topic_model.get_topic(topic_num)[:3]]
        labels[topic_num] = "_".join(words)
    return labels


if __name__ == "__main__":
    add_topic_column()

    articles = get_untopicked_articles()

    if not articles:
        print("No unassigned articles found. Run scraper.py first.")
        exit()

    print(f"Running BERTopic on {len(articles)} articles...\n")

    docs = [a["headline"] + ". " + a["body"][:500] for a in articles]

    n_docs = len(docs)

    if n_docs < 5:
        print(f"Small batch ({n_docs} articles) — using PCA instead of UMAP")
        dim_model = PCA(n_components=min(2, n_docs - 1))
    else:
        dim_model = UMAP(
            n_neighbors=max(2, min(n_docs - 1, 5)),
            n_components=2,
            min_dist=0.0,
            random_state=42
        )

    hdbscan_model = HDBSCAN(
        min_cluster_size=2,
        min_samples=1
    )

    vectorizer = CountVectorizer(stop_words="english")

    topic_model = BERTopic(
        language="english",
        calculate_probabilities=False,
        umap_model=dim_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer,
        verbose=True
    )

    topics, _ = topic_model.fit_transform(docs)

    topic_labels = build_topic_labels(topic_model)

    for article, topic_num in zip(articles, topics):
        topic_label = topic_labels.get(topic_num, f"topic_{topic_num}")
        save_topic(article["id"], topic_label)
        print(f"  [{topic_label}] {article['headline'][:70]}")

    print(f"\n✅ Topics assigned to {len(articles)} articles.")