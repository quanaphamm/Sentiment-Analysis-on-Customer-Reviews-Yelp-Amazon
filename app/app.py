from flask import Flask, render_template, request, jsonify
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import pandas as pd
import os

app = Flask(__name__)

# Load model and tokenizer
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models/distilbert")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}

# Load datasets for search & summary
AMAZON_DF = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/processed/amazon_train.csv"))
YELP_DF = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/processed/yelp_sample.csv"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "").lower()
    source = data.get("source", "")

    if not query or not source:
        return jsonify([])

    if source == "amazon":
        matches = AMAZON_DF["review"].dropna().unique()
    else:
        matches = YELP_DF["review"].dropna().unique()

    filtered = [item for item in matches if query in item.lower()][:10]
    return jsonify(filtered)

@app.route("/summary", methods=["POST"])
def summary():
    data = request.json
    source = data.get("source", "")
    selected = data.get("selected", "")

    if not source or not selected:
        return jsonify({})

    if source == "amazon":
        df = AMAZON_DF[AMAZON_DF["review"].str.contains(selected, case=False, na=False)]
    else:
        df = YELP_DF[YELP_DF["review"].str.contains(selected, case=False, na=False)]

    if df.empty:
        return jsonify({"positive": 0, "neutral": 0, "negative": 0, "suggestion": "Not enough data"})

    sentiment_counts = df["sentiment"].value_counts(normalize=True).to_dict()
    pos = round(sentiment_counts.get("positive", 0) * 100)
    neu = round(sentiment_counts.get("neutral", 0) * 100)
    neg = round(sentiment_counts.get("negative", 0) * 100)

    if pos >= 60:
        suggestion = "✅ Worth Buying" if source == "amazon" else "✅ Should Visit"
    elif neg >= 40:
        suggestion = "❌ Avoid"
    else:
        suggestion = "🤔 Mixed feedback"

    return jsonify({
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "suggestion": suggestion
    })

@app.route("/predict", methods=["POST"])
def predict():
    review = request.json.get("review", "")
    if not review:
        return jsonify({"error": "No review provided"}), 400

    inputs = tokenizer(review, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model(**inputs)
        pred_id = torch.argmax(output.logits, dim=1).item()

    return jsonify({"sentiment": label_map[pred_id]})

if __name__ == "__main__":
    app.run(debug=True)
