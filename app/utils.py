import os
import pandas as pd
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# Load model and tokenizer
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models/distilbert")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}

# Load datasets once
AMAZON_DF = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/processed/amazon_train.csv"))
YELP_DF = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/processed/yelp_sample.csv"))

def get_dataset(source):
    return AMAZON_DF if source == "amazon" else YELP_DF

def search_items(source, query, limit=10):
    df = get_dataset(source)
    matches = df["review"].dropna().unique()
    filtered = [text for text in matches if query.lower() in text.lower()]
    return filtered[:limit]

def summarize_sentiment(source, selected_text):
    df = get_dataset(source)
    matches = df[df["review"].str.contains(selected_text, case=False, na=False)]
    if matches.empty:
        return {"positive": 0, "neutral": 0, "negative": 0, "suggestion": "Not enough data"}

    counts = matches["sentiment"].value_counts(normalize=True).to_dict()
    pos = round(counts.get("positive", 0) * 100)
    neu = round(counts.get("neutral", 0) * 100)
    neg = round(counts.get("negative", 0) * 100)

    if pos >= 60:
        suggestion = "✅ Worth Buying" if source == "amazon" else "✅ Should Visit"
    elif neg >= 40:
        suggestion = "❌ Avoid"
    else:
        suggestion = "🤔 Mixed feedback"

    return {
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "suggestion": suggestion
    }

def predict_sentiment(review_text):
    inputs = tokenizer(review_text, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        output = model(**inputs)
        pred_id = torch.argmax(output.logits, dim=1).item()
    return label_map[pred_id]
