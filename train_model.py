import pandas as pd
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from datasets import Dataset
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_scheduler
from tqdm import tqdm

print("✅ Starting training script")

# ✅ Load preprocessed Amazon review data
df = pd.read_csv("data/processed/amazon_train.csv")
df = df.sample(1000, random_state=42)
df = df[df['sentiment'].isin(['positive', 'neutral', 'negative'])]

# ✅ Encode sentiment labels
label_map = {'negative': 0, 'neutral': 1, 'positive': 2}
df['label'] = df['sentiment'].map(label_map)

# ✅ Split into train and validation sets
train_df, val_df = train_test_split(df[['review', 'label']], test_size=0.1, random_state=42)

# ✅ Convert to HuggingFace Datasets
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# ✅ Tokenize text
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["review"], padding=True, truncation=True)

train_dataset = train_dataset.map(tokenize, batched=True)
val_dataset = val_dataset.map(tokenize, batched=True)
train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
val_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

# ✅ DataLoaders
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True, collate_fn=data_collator)
eval_dataloader = DataLoader(val_dataset, batch_size=16, collate_fn=data_collator)

# ✅ Load model
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ✅ Optimizer and LR Scheduler
optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
num_training_steps = len(train_dataloader) * 2
lr_scheduler = get_scheduler(
    name="linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps
)

# ✅ Training loop
model.train()
for epoch in range(2):
    loop = tqdm(train_dataloader, desc=f"Epoch {epoch+1}")
    for batch in loop:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()

# ✅ Save model
model.save_pretrained("models/distilbert")
tokenizer.save_pretrained("models/distilbert")

print("\n✅ Model training complete and saved to models/distilbert/")