import os 
import sqlite3
import hashlib
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "news.db")

#this function retrieves all articles that have not been scored yet
def get_unscored_articles():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM articles
        WHERE sentiment_label IS NULL
        ORDER BY scraped_at ASC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

#this creates a function that saves the sentiment label and score for a given article
def save_sentiment(article_id, label, score):
    conn = get_connection()
    conn.execute("""
        UPDATE articles
        SET sentiment_label = ?,
            sentiment_score = ?,
            scored_at       = ?
        WHERE id = ?
    """, (label, score, datetime.now().isoformat(), article_id))
    conn.commit()
    conn.close()

#This function creates the database and the articles table if they don't exist
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

#Creates the table that doesn't exist
def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id              TEXT PRIMARY KEY,
            source          TEXT NOT NULL,
            headline        TEXT NOT NULL,
            body            TEXT,
            url             TEXT UNIQUE NOT NULL,
            scraped_at      TEXT,
            sentiment_label TEXT,
            sentiment_score REAL,
            scored_at       TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database ready at: {DB_PATH}")





if __name__ == "__main__":
    init_db()


#url to id function
def url_to_id(url):
    return hashlib.sha256(url.encode()).hexdigest()[:16]

#insertion of article function 
def insert_article(article):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO articles (id, source, headline, body, url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            url_to_id(article["url"]),
            article["source"],
            article["headline"],
            article.get("body", ""),
            article["url"],
            article.get("scraped_at", datetime.now().isoformat()),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate URL — skip silently
    finally:
        conn.close()

def get_all_articles():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM articles
        ORDER BY scraped_at DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

#New function added on Day 4 
def add_topic_column():
    """Add topic column if it doesn't exist yet."""
    conn = get_connection()
    try:
        conn.execute("ALTER TABLE articles ADD COLUMN topic TEXT")
        conn.commit()
        print("✅ Topic column added.")
    except sqlite3.OperationalError:
        print("Topic column already exists — skipping.")
    finally:
        conn.close()

def save_topic(article_id, topic):
    conn = get_connection()
    conn.execute("""
        UPDATE articles
        SET topic = ?
        WHERE id = ?
    """, (topic, article_id))
    conn.commit()
    conn.close()

def get_untopicked_articles():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM articles
        WHERE topic IS NULL
        ORDER BY scraped_at ASC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    scored = conn.execute(
        "SELECT COUNT(*) FROM articles WHERE sentiment_label IS NOT NULL"
    ).fetchone()[0]
    topicked = conn.execute(
        "SELECT COUNT(*) FROM articles WHERE topic IS NOT NULL"
    ).fetchone()[0]

    print(f"\n📊 Database stats")
    print(f"   Total articles : {total}")
    print(f"   Scored         : {scored}")
    print(f"   With topics    : {topicked}")
    conn.close()

if __name__ == "__main__":
    init_db()
    add_topic_column()
    get_stats()

