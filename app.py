import streamlit as st
import plotly.express as px
import pandas as pd
from db import get_all_articles

# Title for the Streamlit app
st.set_page_config(page_title="Jamaican News Sentiment", layout="wide")
st.title("📰 Jamaican News Sentiment Analyzer")

#This function retrieves all articles from the database and displays them in a table
articles = get_all_articles()

if not articles:
    st.warning("No articles found. Run scraper.py and sentiment.py first.")
    st.stop()

df = pd.DataFrame(articles)
df["scraped_at"] = pd.to_datetime(df["scraped_at"])
df = df.dropna(subset=["sentiment_label"])

#Wiring the topics filter

topics = ["All"] + sorted(df["topic"].dropna().unique().tolist())
selected_topic = st.selectbox("Filter by Topic", topics)

if selected_topic != "All":
    df = df[df["topic"] == selected_topic]

#highlighting the frequency of each topic in the dataset
st.subheader("Topic Frequency")

topic_counts = df["topic"].value_counts().reset_index()
topic_counts.columns = ["topic", "count"]

fig0 = px.bar(
    topic_counts,
    x="topic",
    y="count",
    color="topic"
)

st.plotly_chart(fig0, width='stretch')

#A sentiment breakdown chart that shows the distribution of sentiment labels in the dataset
st.subheader("Overall Sentiment Breakdown")

sentiment_counts = df["sentiment_label"].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig = px.pie(
    sentiment_counts,
    names="sentiment",
    values="count",
    color="sentiment",
    color_discrete_map={
        "positive": "#2ecc71",
        "neutral": "#f1c40f",
        "negative": "#e74c3c"
    }
)

# A pie chart that shows the distribution of sentiment labels in the dataset
st.plotly_chart(fig, use_container_width=True)

st.subheader("Sentiment by Source")

source_sentiment = df.groupby(["source", "sentiment_label"]).size().reset_index(name="count")

fig2 = px.bar(
    source_sentiment,
    x="source",
    y="count",
    color="sentiment_label",
    barmode="group",
    color_discrete_map={
        "positive": "#2ecc71",
        "neutral": "#f1c40f",
        "negative": "#e74c3c"
    }
)

st.plotly_chart(fig2, use_container_width=True)

#Adds a table to the Streamlit app that displays the recent articles along with their sentiment labels and confidence scores

st.subheader("Recent Articles")

table = df[["scraped_at", "source", "headline", "sentiment_label", "sentiment_score"]].copy()
table["scraped_at"] = table["scraped_at"].dt.strftime("%Y-%m-%d %H:%M")
table = table.rename(columns={
    "scraped_at": "Date",
    "source": "Source",
    "headline": "Headline",
    "sentiment_label": "Sentiment",
    "sentiment_score": "Confidence"
})

st.dataframe(table, width='stretch')

#

st.subheader("Sentiment Over Time")

df["date"] = df["scraped_at"].dt.date

trend = df.groupby(["date", "sentiment_label"]).size().reset_index(name="count")

fig3 = px.line(
    trend,
    x="date",
    y="count",
    color="sentiment_label",
    markers=True,
    color_discrete_map={
        "positive": "#2ecc71",
        "neutral": "#f1c40f",
        "negative": "#e74c3c"
    }
)

st.plotly_chart(fig3, width='stretch')