import json 
from transformers import pipeline

print("Loading Model (first run downloads ~500MB)...")
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512
)

print("Model Loaded!")
