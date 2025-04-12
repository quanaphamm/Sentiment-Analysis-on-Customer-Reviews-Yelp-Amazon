import os
import bz2
import json
import pandas as pd

# Set base project directory from the script's location
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AMAZON_RAW_DIR = os.path.join(BASE_DIR, "data/raw/amazon")
YELP_RAW_FILE = os.path.join(BASE_DIR, "data/raw/yelp/yelp_academic_dataset_review.json")
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# --- 1. Extract .bz2 files ---
def decompress_bz2(src, dest):
    with bz2.open(src, 'rt') as f_in, open(dest, 'w', encoding='utf-8') as f_out:
        f_out.writelines(f_in)

def extract_amazon_files():
    print("[*] Extracting Amazon .bz2 files...")
    decompress_bz2(os.path.join(AMAZON_RAW_DIR, 'train.ft.txt.bz2'), os.path.join(PROCESSED_DIR, 'amazon_train.txt'))
    decompress_bz2(os.path.join(AMAZON_RAW_DIR, 'test.ft.txt.bz2'), os.path.join(PROCESSED_DIR, 'amazon_test.txt'))

# --- 2. Convert Amazon TXT to CSV ---
def convert_amazon_txt_to_csv(txt_file, csv_file):
    print(f"[*] Converting {txt_file} to CSV...")
    data = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    label, text = parts
                    label = label.replace('__label__', '')
                    data.append([text, label])
                
    df = pd.DataFrame(data, columns=['review', 'sentiment'])
    df.to_csv(csv_file, index=False)

# --- 3. Process Yelp JSON ---
def process_yelp_json(sample_size=100_000):
    print(f"[*] Sampling Yelp reviews from JSON...")
    data = []
    with open(YELP_RAW_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            review = json.loads(line)
            stars = review['stars']
            sentiment = 'positive' if stars > 3 else 'negative' if stars < 3 else 'neutral'
            data.append([review['business_id'], review['text'], stars, sentiment])
    df = pd.DataFrame(data, columns=['business_id', 'review', 'stars', 'sentiment'])
    df.to_csv(os.path.join(PROCESSED_DIR, 'yelp_sample.csv'), index=False)

# --- Run All ---
if __name__ == "__main__":
    extract_amazon_files()
    convert_amazon_txt_to_csv(os.path.join(PROCESSED_DIR, 'amazon_train.txt'), os.path.join(PROCESSED_DIR, 'amazon_train.csv'))
    convert_amazon_txt_to_csv(os.path.join(PROCESSED_DIR, 'amazon_test.txt'), os.path.join(PROCESSED_DIR, 'amazon_test.csv'))
    process_yelp_json()
    print("\n✅ All datasets processed and saved in data/processed/")
