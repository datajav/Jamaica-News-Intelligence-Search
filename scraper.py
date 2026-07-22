import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 20  # seconds — Jamaican sites can be slow


# Helper function to fetch a homepage with error handling

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


# Scraper functions for each news source

def scrape_nationwide(max_articles=10):
    """Scrape Nationwide News Network Jamaica (nationwideradiojm.com)."""
    base_url = "https://nationwideradiojm.com"
    articles = []

    print(f"[Nationwide] Fetching homepage...")
    soup = fetch_homepage(base_url, "Nationwide")
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

    print(f"[Nationwide] Found {len(links)} article links. Fetching content...")
    for url in links:
        article = scrape_article(url, source="nationwide")
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


#  Article parser 

def scrape_article(url, source):
    """Generic article scraper — extracts headline and body text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Headline — try common tags in order of preference
        headline = None
        for tag in ["h1", "h2"]:
            el = soup.find(tag)
            if el and len(el.get_text(strip=True)) > 10:
                headline = el.get_text(strip=True)
                break

        if not headline:
            return None

        # Body — grab all paragraphs and join
        paragraphs = soup.find_all("p")
        body = " ".join(
            p.get_text(strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 40
        )

        if len(body) < 100:
            return None  # Skip pages with no real article content

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


# Run 

if __name__ == "__main__":
    all_articles = []

    all_articles += scrape_nationwide(max_articles=5)
    all_articles += scrape_gleaner(max_articles=5)
    all_articles += scrape_observer(max_articles=5)

    # Save to JSON for now (database comes next)
    output_file = "articles.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    print(f"\n Scraped {len(all_articles)} articles → saved to {output_file}")

    if all_articles:
        sample = all_articles[0]
        print(f"\nSample article:")
        print(f"  Source   : {sample['source']}")
        print(f"  Headline : {sample['headline']}")
        print(f"  Body     : {sample['body'][:200]}...")
    else:
        print("\n  No articles scraped — check the error messages above.")