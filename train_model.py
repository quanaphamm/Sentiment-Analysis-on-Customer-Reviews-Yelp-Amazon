import os
import pandas as pd
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    DataCollatorWithPadding,
    get_scheduler,
)
from sklearn.model_selection import train_test_split
from datasets import Dataset
from torch.utils.data import DataLoader
from torch.optim import AdamW
from tqdm import tqdm
import tempfile

# ✅ Load & Preprocess Yelp data
df = pd.read_csv("data/processed/yelp_sample.csv")
df = df[["product_or_place", "review", "sentiment"]]
label_map = {"negative": 0, "neutral": 1, "positive": 2}
df["label"] = df["sentiment"].map(label_map)
df = df.sample(500, random_state=42)  # small set for testing

# ✅ Train/Validation Split
train_df, val_df = train_test_split(df[["review", "label"]], test_size=0.1, random_state=42)

# ✅ Convert to Hugging Face Dataset
train_dataset = Dataset.from_pandas(train_df.reset_index(drop=True))
val_dataset = Dataset.from_pandas(val_df.reset_index(drop=True))

# ✅ Tokenization
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
def tokenize(batch): return tokenizer(batch["review"], padding=True, truncation=True)
train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=["review"])
val_dataset = val_dataset.map(tokenize, batched=True, remove_columns=["review"])

train_dataset.set_format(type="torch")
val_dataset.set_format(type="torch")

# ✅ Data Loaders
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, collate_fn=data_collator)
val_loader = DataLoader(val_dataset, batch_size=16, collate_fn=data_collator)

# ✅ Model Setup
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ✅ Optimizer & Scheduler
optimizer = AdamW(model.parameters(), lr=5e-5)
num_training_steps = len(train_loader) * 2
lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

# ✅ Training Loop
for epoch in range(2):
    model.train()
    loop = tqdm(train_loader, desc=f"Epoch {epoch+1}")
    for batch in loop:
        batch = {k: v.to(device) for k, v in batch.items()}
        output = model(**batch)
        loss = output.loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        loop.set_postfix(loss=loss.item())

# ✅ Save model safely
save_dir = "models/distilbert"

try:
    os.makedirs(save_dir, exist_ok=True)
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    print(f"\n✅ Model trained and saved to {save_dir}/")

except Exception as e:
    print(f"\n⚠️ Error saving model to {save_dir}: {e}")
    fallback_dir = tempfile.mkdtemp()
    model.save_pretrained(fallback_dir)
    tokenizer.save_pretrained(fallback_dir)
    print(f"✅ Model saved to temporary path instead: {fallback_dir}")

