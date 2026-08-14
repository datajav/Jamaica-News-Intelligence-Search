# Jamaican News Sentiment Analyzer

A natural language processing pipeline that scrapes articles from major Jamaican news outlets, performs sentiment analysis, and surfaces topic trends over time — revealing how different outlets frame stories around crime, politics, tourism, and the economy.

**Data sources:** Jamaica Gleaner · Jamaica Observer · Nationwide News Network

---

## Features

- **Automated scraping** — daily article collection with scheduling
- **Sentiment analysis** — transformer-based scoring per article and outlet
- **Topic modeling** — unsupervised discovery of recurring themes using BERTopic
- **Named entity recognition** — tracks politicians, places, and organizations
- **Interactive dashboard** — sentiment trends, topic heatmaps, and outlet comparisons via Streamlit

---

## Tech Stack

| Layer | Tools |
|---|---|
| Scraping | `requests`, `BeautifulSoup4`, `schedule` |
| NLP | `spaCy`, `HuggingFace Transformers`, `BERTopic` |
| Sentiment model | `cardiffnlp/twitter-roberta-base-sentiment` |
| Storage | `SQLite` (dev) / `PostgreSQL` (production) |
| Dashboard | `Streamlit`, `Plotly` |

---

## Project Structure

```
jamaican-news-sentiment/
├── scraper/
│   ├── gleaner.py          # Gleaner-specific scraper
│   ├── observer.py         # Observer-specific scraper
│   ├── nationwide.py       # Nationwide News Network scraper
│   └── base.py             # Shared scraping logic
├── pipeline/
│   ├── cleaner.py          # Text preprocessing with spaCy
│   ├── sentiment.py        # HuggingFace sentiment scoring
│   ├── topics.py           # BERTopic topic modeling
│   └── entities.py         # NER tagging
├── db/
│   ├── models.py           # Database schema
│   └── db.py               # Read/write helpers
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── data/                   # Local SQLite database (gitignored)
├── notebooks/              # Exploratory analysis
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/jamaican-news-sentiment.git
cd jamaican-news-sentiment

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Environment setup

```bash
cp .env.example .env
# Edit .env with your config (DB path, scrape interval, etc.)
```

---

## Usage

### Run the scraper (one-time)

```bash
python scraper/run.py --source all
```

### Run the scraper on a schedule

```bash
python scraper/scheduler.py  # Runs daily by default
```

### Process articles through the NLP pipeline

```bash
python pipeline/run.py --batch 100
```

### Launch the dashboard

```bash
streamlit run dashboard/app.py
```

---

## Dashboard Views

- **Sentiment over time** — rolling average sentiment per outlet, filterable by topic
- **Topic heatmap** — which themes dominated each week and in which outlet
- **Outlet comparison** — side-by-side framing of the same story across Gleaner, Observer, and Nationwide
- **Entity spotlight** — search a politician, place, or organization and view their sentiment arc

---

## Database Schema

```
articles
├── id             TEXT  PRIMARY KEY
├── source         TEXT  (gleaner | observer | nationwide)
├── headline       TEXT
├── body           TEXT
├── url            TEXT
├── published_at   TEXT
├── category       TEXT
├── sentiment_label TEXT  (positive | neutral | negative)
├── sentiment_score REAL
├── topics         TEXT  (JSON array)
└── entities       TEXT  (JSON array)
```

---

## Roadmap

- [x] Add Nationwide News Network as a source
- [ ] Add CVM TV as a source
- [ ] Patois-aware sentiment fine-tuning
- [ ] Weekly email digest of top trending topics
- [ ] Public deployment on Streamlit Cloud
- [ ] Twitter/X integration for social sentiment comparison

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## License

[MIT](LICENSE)

---

> Built in Jamaica 🇯🇲 — tracking the stories that shape the island.