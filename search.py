import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from db import get_all_embeddings, get_connection

MODEL_NAME = "all-MiniLM-L6-v2"

# ── Cached model and index — loads once, reused for every search ──────────────

_model = None
_index_cache = None
_ids_cache = None


def get_model():
    global _model
    if _model is None:
        print("Loading search model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Search model ready.")
    return _model


def load_index():
    """Load all vectors from the database into a FAISS index."""
    embeddings = get_all_embeddings()

    if not embeddings:
        return None, []

    ids = []
    vectors = []

    for article_id, vector_bytes in embeddings:
        vector = np.frombuffer(vector_bytes, dtype=np.float32)
        ids.append(article_id)
        vectors.append(vector)

    matrix = np.vstack(vectors).astype("float32")
    faiss.normalize_L2(matrix)

    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)

    return index, ids


def get_index():
    """Return cached index — only builds once per session."""
    global _index_cache, _ids_cache
    if _index_cache is not None:
        return _index_cache, _ids_cache
    _index_cache, _ids_cache = load_index()
    return _index_cache, _ids_cache


def search(query, top_k=10):
    """Search articles by semantic similarity to a query string."""
    model = get_model()
    index, ids = get_index()

    if index is None:
        return []

    query_vector = model.encode(query).astype("float32")
    query_vector = query_vector.reshape(1, -1)
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, top_k)

    results = []
    conn = get_connection()

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        article_id = ids[idx]
        row = conn.execute(
            "SELECT * FROM articles WHERE id = ?", (article_id,)
        ).fetchone()
        if row:
            result = dict(row)
            result["relevance"] = round(float(score) * 100, 1)
            results.append(result)

    conn.close()
    return results