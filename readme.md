# 📰 Jamaica News Intelligence Search

A semantic search engine over Jamaican news and institutional publications — find articles, reports, and press releases by meaning, not just keywords. Built for researchers, students, journalists, and policy analysts.

**News sources:** Jamaica Gleaner · Jamaica Observer · Jamaica Information Service

**Institutional sources:** Planning Institute of Jamaica (PIOJ) · Bank of Jamaica (BOJ) · Statistical Institute of Jamaica (STATIN)

---

## What it does

Traditional keyword search returns articles that contain your exact words. This engine understands *meaning* — search for "government response to flooding in western Jamaica" and it will surface relevant articles even if they use different words like "disaster relief", "parish council", or "St. James".

Under the hood it converts every article into a semantic vector using a sentence transformer model, stores those vectors, and at search time finds the articles whose meaning is closest to your query using FAISS similarity search.

---

## Features

- **Semantic search** — find articles by meaning using sentence transformers and FAISS
- **Multi-source indexing** — news outlets and official government publications in one place
- **Sentiment context** — every result shows whether the coverage is positive, neutral, or negative
- **Topic context** — BERTopic-assigned topic labels appear alongside each result
- **Sidebar filters** — narrow results by source or sentiment label
- **Deduplication** — SHA256 URL hashing ensures no article appears twice
- **Daily pipeline** — scrape, score, assign topics, and embed new articles each day

---

## Tech Stack

| Layer | Tools |
|---|---|
| Scraping | `requests`, `BeautifulSoup4` |
| Sentiment model | `cardiffnlp/twitter-roberta-base-sentiment-latest` via HuggingFace |
| Topic modeling | `BERTopic`, `sklearn HDBSCAN`, `sentence-transformers`, `umap-learn` |
| Embeddings | `all-MiniLM-L6-v2` via `sentence-transformers` |
| Vector search | `FAISS` (faiss-cpu) |
| Storage | `SQLite` (Python built-in `sqlite3`) |
| Dashboard | `Streamlit`, custom CSS |

---

## Project Structure

```
Jamaican-News-Sentiment-Analyzer/
├── scraper.py      # Scrapes all 6 sources → saves to news.db
├── sentiment.py    # Scores unscored articles → writes labels + scores to news.db
├── topics.py       # Runs BERTopic on unassigned articles → writes topic labels to news.db
├── embed.py        # Generates sentence vectors → saves to embeddings table in news.db
├── search.py       # FAISS-powered semantic search engine
├── db.py           # All database reads, writes, and schema management
├── app.py          # Streamlit search interface
├── run.bat         # One-click dashboard launcher (Windows)
├── news.db         # SQLite database (gitignored)
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/Jamaican-News-Sentiment-Analyzer.git
cd Jamaican-News-Sentiment-Analyzer

# Install dependencies
pip install requests beautifulsoup4 streamlit plotly pandas bertopic \
    sentence-transformers umap-learn scikit-learn transformers torch faiss-cpu
```

---

## Usage

### Daily pipeline

Run these four commands each day to collect and process new content:

```bash
# 1. Scrape new articles from all 6 sources
python scraper.py

# 2. Score any unscored articles with sentiment analysis
python sentiment.py

# 3. Assign topic labels to any unassigned articles
python topics.py

# 4. Generate semantic vectors for new articles
python embed.py
```

### Launch the search interface

**Windows — double-click `run.bat`**

Or from the terminal:

```bash
python -m streamlit run app.py
```

---

## How it works

```
Query: "economic impact of drought on Jamaican farmers"
         │
         ▼
  Sentence Transformer
  (all-MiniLM-L6-v2)
         │
         ▼
   Query vector [0.23, -0.41, 0.87 ...]
         │
         ▼
  FAISS similarity search
  against 500+ article vectors
         │
         ▼
  Top 10 most semantically
  similar articles ranked
  by relevance score
```

---

## Database Schema

```
articles
├── id              TEXT  PRIMARY KEY    — SHA256 hash of URL (deduplication key)
├── source          TEXT                 — gleaner | observer | nationwide | pioj | boj | statin
├── headline        TEXT
├── body            TEXT
├── url             TEXT  UNIQUE
├── scraped_at      TEXT                 — ISO timestamp
├── sentiment_label TEXT                 — positive | neutral | negative
├── sentiment_score REAL                 — model confidence (0.0 – 1.0)
├── scored_at       TEXT                 — ISO timestamp, NULL until scored
└── topic           TEXT                 — BERTopic keyword label, NULL until assigned

embeddings
├── article_id      TEXT  PRIMARY KEY    — references articles.id
└── vector          BLOB                 — serialized float32 numpy array
```

---

## Roadmap

- [x] Scraper — Gleaner, Observer, Nationwide News Network
- [x] Institutional scraper — PIOJ, BOJ, STATIN
- [x] SQLite persistence with SHA256 deduplication
- [x] Sentiment analysis pipeline (RoBERTa)
- [x] BERTopic topic modeling with human-readable labels
- [x] Sentence embeddings (all-MiniLM-L6-v2)
- [x] FAISS semantic search engine
- [x] Streamlit search interface with filters
- [ ] Academic sources — UWI Mona Institutional Repository, Caribbean Quarterly
- [ ] Named entity recognition — track politicians and places over time
- [ ] Deployment on Streamlit Cloud
- [ ] CVM TV as an additional news source

---

## License

[MIT](LICENSE)

---

> Built in Jamaica 🇯🇲 — making Jamaican knowledge searchable.