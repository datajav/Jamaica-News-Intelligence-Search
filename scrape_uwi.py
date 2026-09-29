import requests
from datetime import datetime
from db import init_db, insert_article

BASE_URL = "https://uwispace.sta.uwi.edu/server/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JamaicaNewsSearch/1.0)"
}

def fetch_items(query="Jamaica", page=0, size=10):
    """Search UWISpace for items matching a query."""
    url = f"{BASE_URL}/discover/search/objects"
    params = {
        "query": query,
        "page": page,
        "size": size
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.json()


def extract_metadata(item):
    """Pull title, abstract, date and URI from a DSpace item."""
    metadata = item.get("metadata", {})

    def get_field(field):
        values = metadata.get(field, [])
        return values[0]["value"] if values else None

    title    = get_field("dc.title")
    abstract = get_field("dc.description.abstract") or get_field("dc.description")
    date     = get_field("dc.date.issued") or get_field("dc.date.accessioned")
    uri      = get_field("dc.identifier.uri")

    return title, abstract, date, uri


def scrape_uwispace(query="Jamaica", max_pages=3, size=10):
    """Harvest UWISpace metadata for Jamaica-related publications."""
    articles = []
    print(f"[UWISpace] Searching for '{query}'...")

    for page in range(max_pages):
        try:
            data = fetch_items(query=query, page=page, size=size)
            objects = (
                data.get("_embedded", {})
                    .get("searchResult", {})
                    .get("_embedded", {})
                    .get("objects", [])
            )

            if not objects:
                print(f"[UWISpace] No more results at page {page}.")
                break

            for obj in objects:
                item = obj.get("_embedded", {}).get("indexableObject", {})
                title, abstract, date, uri = extract_metadata(item)

                if not title or not uri:
                    continue

                # Use abstract as body — enough for semantic search
                body = abstract or title

                articles.append({
                    "source":     "uwispace",
                    "headline":   title,
                    "body":       body[:3000],
                    "url":        uri,
                    "scraped_at": datetime.now().isoformat(),
                })
                print(f"  ✓ {title[:70]}...")

        except Exception as e:
            print(f"  ✗ Page {page} failed — {e}")
            break

    return articles


if __name__ == "__main__":
    init_db()

    articles = scrape_uwispace(query="Jamaica", max_pages=3, size=10)

    new_count = 0
    dupe_count = 0

    for article in articles:
        inserted = insert_article(article)
        if inserted:
            new_count += 1
        else:
            dupe_count += 1

    print(f"\n✅ Done — {new_count} new articles saved, {dupe_count} duplicates skipped")