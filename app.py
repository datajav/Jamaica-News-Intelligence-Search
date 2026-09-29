import streamlit as st
import pandas as pd
from search import search
from db import get_all_articles

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Jamaica News Search",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styling ───────────────────────────────────────────────────────────────────

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Serif+4:wght@400;600&display=swap');

        [data-testid="stAppViewContainer"] { background-color: #f5f3ee; }
        [data-testid="stHeader"]           { background-color: #f5f3ee; }
        [data-testid="stSidebar"]          { background-color: #ede9e0; border-right: 1px solid #ccc8be; }
        [data-testid="stSidebar"] *        { color: #4a4843 !important; }

        html, body, [class*="css"] {
            font-family: 'Source Serif 4', Georgia, serif;
            color: #1a1916;
        }
        h1, h2, h3 {
            font-family: 'Playfair Display', Georgia, serif;
            color: #1a3a5c !important;
        }
        .result-card {
            background-color: #ffffff;
            border: 1px solid #ccc8be;
            border-left: 4px solid #1a3a5c;
            border-radius: 4px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
        }
        .result-headline {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.1rem;
            color: #1a3a5c;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        .result-meta {
            font-size: 0.85rem;
            color: #888680;
            margin-bottom: 0.4rem;
        }
        .result-relevance {
            font-size: 0.85rem;
            color: #4a4843;
        }
        .tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.78rem;
            margin-right: 4px;
        }
        .tag-positive  { background-color: #e8edf3; color: #1a3a5c; }
        .tag-neutral   { background-color: #f0efed; color: #4a4843; }
        .tag-negative  { background-color: #f3ebe8; color: #7a3b1e; }
        .tag-topic     { background-color: #ede9e0; color: #4a4843; }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar filters ───────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filters")

    all_articles = get_all_articles()
    df = pd.DataFrame(all_articles)

    sources = ["All"] + sorted(df["source"].dropna().unique().tolist())
    selected_source = st.selectbox("Source", sources)

    sentiments = ["All", "positive", "neutral", "negative"]
    selected_sentiment = st.selectbox("Sentiment", sentiments)

    top_k = st.slider("Number of results", min_value=5, max_value=30, value=10)

    st.markdown("---")
    st.caption(f"📚 {len(df)} articles indexed")
    st.caption("Sources: Gleaner · Observer · JIS · BOJ · STATIN · PIOJ")

# ── Main ──────────────────────────────────────────────────────────────────────

st.title("📰 Jamaica News Intelligence Search")
st.markdown(
    "<p style='color:#4a4843; font-family:Source Serif 4,Georgia,serif; font-size:1.1rem;'>"
    "Semantic search across Jamaican news — find articles by meaning, not just keywords.</p>",
    unsafe_allow_html=True
)
st.markdown("<hr style='border:1px solid #ccc8be; margin-bottom:1.5rem;'>", unsafe_allow_html=True)

query = st.text_input(
    "",
    placeholder="Lets get it started, search here...",
    label_visibility="collapsed"
)

if st.button("🔍 Search", use_container_width=True) or query:
    if not query.strip():
        st.info("Enter a search query above.")
    else:
        with st.spinner("Searching..."):
            results = search(query, top_k=top_k * 2)

            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    unique_results.append(r)

            # Apply sidebar filters
            if selected_source != "All":
                unique_results = [r for r in unique_results if r["source"] == selected_source]
            if selected_sentiment != "All":
                unique_results = [r for r in unique_results if r["sentiment_label"] == selected_sentiment]

            unique_results = unique_results[:top_k]

        if not unique_results:
            st.warning("No results found. Try a different query or adjust the filters.")
        else:
            st.markdown(f"**{len(unique_results)} results** for *{query}*")
            st.markdown("<br>", unsafe_allow_html=True)

            for r in unique_results:
                sentiment = r.get("sentiment_label", "neutral")
                topic = r.get("topic", "")
                date = r.get("scraped_at", "")[:10]
                source = r.get("source", "").upper()
                relevance = r.get("relevance", 0)
                headline = r.get("headline", "")
                url = r.get("url", "#")

                tag_class = f"tag-{sentiment}"
                sentiment_emoji = {"positive": "🔵", "neutral": "⚪", "negative": "🟤"}.get(sentiment, "")

                st.markdown(f"""
                    <div class="result-card">
                        <div class="result-headline">
                            <a href="{url}" target="_blank" style="color:#1a3a5c; text-decoration:none;">{headline}</a>
                        </div>
                        <div class="result-meta">{source} · {date}</div>
                        <div>
                            <span class="tag {tag_class}">{sentiment_emoji} {sentiment}</span>
                            <span class="tag tag-topic">🏷 {topic}</span>
                        </div>
                        <div class="result-relevance" style="margin-top:0.5rem;">
                            Relevance: {relevance}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)