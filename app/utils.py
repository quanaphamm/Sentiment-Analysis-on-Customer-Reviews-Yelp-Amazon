import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# ✅ Load model and tokenizer only once
def load_model(model_path="models/distilbert"):
    tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device

# ✅ Run prediction
def predict_sentiment(review_text, tokenizer, model, device):
    label_map = {0: "negative", 1: "neutral", 2: "positive"}

    # Tokenize input
    inputs = tokenizer(review_text, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        predicted_class = torch.argmax(probs, dim=1).item()
        label = label_map[predicted_class]
        confidence = round(probs[0][predicted_class].item(), 4)

    return label, confidence
