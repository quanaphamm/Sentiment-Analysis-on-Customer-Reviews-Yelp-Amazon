import pandas as pd
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from sklearn.model_selection import train_test_split
from datasets import Dataset

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

# ✅ Load model
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

# ✅ Set training parameters
training_args = TrainingArguments(
    output_dir="./models/distilbert",
    num_train_epochs=1,
    per_device_train_batch_size=16
)


# ✅ Initialize trainer
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,  
    data_collator=data_collator  
)

# ✅ Train model
trainer.train()

# ✅ Save model & tokenizer
model.save_pretrained("models/distilbert")
tokenizer.save_pretrained("models/distilbert")

print("\n✅ Model training complete and saved to models/distilbert/")
