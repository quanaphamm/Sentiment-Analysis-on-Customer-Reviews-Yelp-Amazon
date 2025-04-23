from flask import Flask, render_template, request, jsonify
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import pandas as pd
import os

app = Flask(__name__)

# Load trained model and tokenizer
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models/distilbert")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}

# Load Yelp data
YELP_DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/processed/yelp_sample.csv")
df = pd.read_csv(YELP_DATA_PATH)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "").lower()

    all_places = df["product_or_place"].dropna().unique()
    matches = [place for place in all_places if query in place.lower()]
    return jsonify(matches[:10])

@app.route("/summary", methods=["POST"])
def summary():
    data = request.get_json()
    selected = data.get("selected", "")

    filtered = df[df["product_or_place"].str.lower() == selected.lower()]
    if filtered.empty:
        return jsonify({
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "suggestion": "Not enough data",
            "reviews": []
        })

    counts = filtered["sentiment"].value_counts(normalize=True).to_dict()
    pos = round(counts.get("positive", 0) * 100)
    neu = round(counts.get("neutral", 0) * 100)
    neg = round(counts.get("negative", 0) * 100)

    if pos >= 60:
        suggestion = "✅ Should Visit"
    elif neg >= 40:
        suggestion = "❌ Avoid"
    else:
        suggestion = "🤔 Mixed feedback"

    top_reviews = filtered[["review", "sentiment"]].head(10).to_dict(orient="records")

    return jsonify({
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "suggestion": suggestion,
        "reviews": top_reviews
    })

@app.route("/predict", methods=["POST"])
def predict():
    review = request.get_json().get("review", "")

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
