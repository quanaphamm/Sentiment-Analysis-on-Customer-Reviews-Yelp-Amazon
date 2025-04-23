from flask import Flask, render_template, request, jsonify
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import pandas as pd
import os

app = Flask(__name__)

# --- Load model & tokenizer ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models/distilbert")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}

# --- Load Yelp dataset ---
YELP_DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/processed/yelp_sample.csv")
df = pd.read_csv(YELP_DATA_PATH)

@app.route("/")
def index():
    return render_template("index.html")

# --- Autocomplete search ---
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "").lower()

    all_places = df["product_or_place"].dropna().unique()
    matches = [place for place in all_places if query in place.lower()]
    return jsonify(matches[:10])

# --- Show summary + recent reviews ---
@app.route("/summary", methods=["POST"])
def summary():
    data = request.get_json()
    selected = data.get("selected", "")

    filtered = df[df["product_or_place"].str.lower() == selected.lower()]
    if filtered.empty:
        return jsonify({
            "positive": 0, "neutral": 0, "negative": 0,
            "suggestion": "Not enough data",
            "reviews": []
        })

    counts = filtered["sentiment"].value_counts(normalize=True).to_dict()
    pos = round(counts.get("positive", 0) * 100)
    neu = round(counts.get("neutral", 0) * 100)
    neg = round(counts.get("negative", 0) * 100)

    # ✅ Smart suggestion logic
    if neg > pos and neg > neu:
        suggestion = "❌ Avoid"
    else:
        suggestion = "✅ Should Visit"

    # ✅ Newest 10 reviews (reverse order)
    top_reviews = (
        filtered[["review", "sentiment"]]
        .iloc[::-1]
        .head(10)
        .to_dict(orient="records")
    )

    return jsonify({
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "suggestion": suggestion,
        "reviews": top_reviews
    })

# --- Predict sentiment + persist review ---
@app.route("/predict", methods=["POST"])
def predict():
    content = request.get_json()
    review = content.get("review", "")
    selected = content.get("selected", "")

    if not review or not selected:
        return jsonify({"error": "Missing review or place name"}), 400

    # Predict sentiment
    inputs = tokenizer(review, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        output = model(**inputs)
        pred_id = torch.argmax(output.logits, dim=1).item()
        sentiment = label_map[pred_id]

    # Save review to CSV
    new_row = pd.DataFrame([{
        "product_or_place": selected,
        "review": review,
        "stars": "",  # Optional
        "sentiment": sentiment
    }])
    new_row.to_csv(YELP_DATA_PATH, mode='a', header=False, index=False)

    # Update in-memory DataFrame
    global df
    df = pd.read_csv(YELP_DATA_PATH)

    return jsonify({"sentiment": sentiment})

if __name__ == "__main__":
    app.run(debug=True)
