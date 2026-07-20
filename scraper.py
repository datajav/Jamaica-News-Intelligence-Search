import requests 
from bs4 import BeautifulSoup
import json
from datetime import datetime

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
}

def scrape_loop_news(max_articles=10):
    """This Scrapes headlines and article text from Radio Jamaica."""
    base_url = "https://radiojamaicanewsonline.com"
    articles = []

    print (f"[RJR News] Fetching homepage....")
    resp = requests.get(base_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True): 
        href = a["href"]
        #RJR artticles URLs that would contain years or category slugs 
        if any (seg in href for seg in ["/news", "/business", "/sports", "/entertainment"]):
            full_url = href if href.startswith("http") else base_url + href
            if full_url not in links and full_url != base_url:
                links.append(full_url)
        if len(links) >= max_articles:
            break

        print(f"[RJR News]Found {len(links)} article links. Scraping articles....")

        for url in links:
            article = scrape_article(url, source="RJR")
            if article:
                articles.append(article)
                print(f" completed{article['headline'][:70]}")

        return articles
    
