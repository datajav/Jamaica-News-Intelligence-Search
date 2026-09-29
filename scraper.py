import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from db import init_db, insert_article
from scrape_uwi import scrape_uwispace

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 20


# ── Helper ────────────────────────────────────────────────────────────────────

def fetch_homepage(url, label):
    """Safely fetch a homepage. Returns BeautifulSoup or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.SSLError:
        print(f"  ✗ [{label}] SSL error — site may be blocking scrapers")
    except requests.exceptions.Timeout:
        print(f"  ✗ [{label}] Timed out after {TIMEOUT}s — site unreachable")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ [{label}] Connection failed — check your internet or the URL")
    except Exception as e:
        print(f"  ✗ [{label}] Unexpected error — {e}")
    return None


# ── News scrapers ─────────────────────────────────────────────────────────────

def scrape_jis(max_articles=10):
    """Scrape Jamaica Information Service (https://jis.gov.jm/)."""
    base_url = "https://jis.gov.jm/"
    articles = []

    print(f"[JIS] Fetching homepage...")
    soup = fetch_homepage(base_url, "JIS")
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(seg in href for seg in ["/news/", "/local/", "/regional/", "/sports/"]):
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links and full_url != base_url:
                links.append(full_url)
        if len(links) >= max_articles:
            break

    print(f"[JIS] Found {len(links)} article links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="jis")
        if article:
            articles.append(article)
            print(f"  ✓ {article['headline'][:70]}...")

    return articles


def scrape_gleaner(max_articles=10):
    """Scrape Jamaica Gleaner (jamaica-gleaner.com)."""
    base_url = "https://jamaica-gleaner.com"
    articles = []

    print(f"[Gleaner] Fetching homepage...")
    soup = fetch_homepage(base_url, "Gleaner")
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/article/" in href:
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links:
                links.append(full_url)
        if len(links) >= max_articles:
            break

    print(f"[Gleaner] Found {len(links)} article links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="gleaner")
        if article:
            articles.append(article)
            print(f"  ✓ {article['headline'][:70]}...")

    return articles


def scrape_observer(max_articles=10):
    """Scrape Jamaica Observer (jamaicaobserver.com)."""
    base_url = "https://www.jamaicaobserver.com"
    articles = []

    print(f"[Observer] Fetching homepage...")
    soup = fetch_homepage(base_url, "Observer")
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(seg in href for seg in ["/news/", "/business/", "/sport/"]):
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links:
                links.append(full_url)
        if len(links) >= max_articles:
            break

    print(f"[Observer] Found {len(links)} article links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="observer")
        if article:
            articles.append(article)
            print(f"  ✓ {article['headline'][:70]}...")

    return articles


# ── Institutional scrapers ────────────────────────────────────────────────────

def scrape_pioj(max_articles=10):
    """Scrape Planning Institute of Jamaica (pioj.gov.jm)."""
    base_url = "https://pioj.gov.jm"
    articles = []

    print(f"[PIOJ] Fetching homepage...")
    soup = fetch_homepage(base_url, "PIOJ")
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(seg in href for seg in ["/news/", "/publications/", "/press-release/", "/reports/"]):
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links and full_url != base_url:
                links.append(full_url)
        if len(links) >= max_articles:
            break

    print(f"[PIOJ] Found {len(links)} links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="pioj")
        if article:
            articles.append(article)
            print(f"  ✓ {article['headline'][:70]}...")

    return articles


def scrape_boj(max_articles=10):
    """Scrape Bank of Jamaica (boj.org.jm)."""
    base_url = "https://boj.org.jm"
    articles = []

    print(f"[BOJ] Fetching homepage...")
    soup = fetch_homepage(base_url, "BOJ")
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(seg in href for seg in ["/news/", "/press-releases/", "/speeches/", "/publications/"]):
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links and full_url != base_url:
                links.append(full_url)
        if len(links) >= max_articles:
            break

    print(f"[BOJ] Found {len(links)} links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="boj")
        if article:
            articles.append(article)
            print(f"  ✓ {article['headline'][:70]}...")

    return articles


def scrape_statin(max_articles=10):
    """Scrape Statistical Institute of Jamaica (statinja.gov.jm)."""
    base_url = "https://statinja.gov.jm"
    articles = []

    print(f"[STATIN] Fetching homepage...")
    soup = fetch_homepage(base_url, "STATIN")
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(seg in href for seg in ["/news/", "/press-releases/", "/publications/", "/releases/"]):
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links and full_url != base_url:
                links.append(full_url)
        if len(links) >= max_articles:
            break

    print(f"[STATIN] Found {len(links)} links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="statin")
        if article:
            articles.append(article)
            print(f"  ✓ {article['headline'][:70]}...")

    return articles


# ── Article parser ────────────────────────────────────────────────────────────

def scrape_article(url, source):
    """Generic article scraper — extracts headline and body text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")

        headline = None
        for tag in ["h1", "h2"]:
            el = soup.find(tag)
            if el and len(el.get_text(strip=True)) > 10:
                headline = el.get_text(strip=True)
                break

        if not headline:
            return None

        paragraphs = soup.find_all("p")
        body = " ".join(
            p.get_text(strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 40
        )

        if len(body) < 100:
            return None

        return {
            "source": source,
            "headline": headline,
            "body": body[:3000],
            "url": url,
            "scraped_at": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"  ✗ Failed {url[:60]} — {e}")
        return None


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    all_articles = []

    # News sources
    all_articles += scrape_jis(max_articles=5)
    all_articles += scrape_gleaner(max_articles=5)
    all_articles += scrape_observer(max_articles=5)

    # Institutional sources
    all_articles += scrape_pioj(max_articles=5)
    all_articles += scrape_boj(max_articles=5)
    all_articles += scrape_statin(max_articles=5)

    new_count = 0
    dupe_count = 0

    for article in all_articles:
        inserted = insert_article(article)
        if inserted:
            new_count += 1
        else:
            dupe_count += 1

    print(f"\n✅ Done — {new_count} new articles saved, {dupe_count} duplicates skipped")