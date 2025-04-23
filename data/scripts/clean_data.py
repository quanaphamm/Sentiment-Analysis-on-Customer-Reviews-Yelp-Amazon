import os
import json
import pandas as pd

# Set base project directory from the script's location
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
YELP_RAW_FILE = os.path.join(BASE_DIR, "data/raw/yelp/yelp_academic_dataset_review.json")
YELP_BUSINESS_FILE = os.path.join(BASE_DIR, "data/raw/yelp/yelp_academic_dataset_business.json")
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# --- Process Yelp JSON ---
def process_yelp_json(sample_size=100_000):
    print(f"[*] Sampling Yelp reviews from JSON...")
    data = []
    with open(YELP_BUSINESS_FILE, 'r', encoding='utf-8') as f:
        business_lookup = {}
        for line in f:
            entry = json.loads(line)
            business_lookup[entry['business_id']] = entry['name']

    with open(YELP_RAW_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            review = json.loads(line)
            stars = review['stars']
            sentiment = 'positive' if stars > 3 else 'negative' if stars < 3 else 'neutral'
            business_id = review['business_id']
            business_name = business_lookup.get(business_id, "Unknown")
            data.append([business_name.strip(), review['text'].strip(), stars, sentiment])

    df = pd.DataFrame(data, columns=['product_or_place', 'review', 'stars', 'sentiment'])
    df.to_csv(os.path.join(PROCESSED_DIR, 'yelp_sample.csv'), index=False)

# --- Run Only Yelp Data Processing ---
if __name__ == "__main__":
    process_yelp_json()
    print("\n✅ Yelp dataset processed and saved to data/processed/yelp_sample.csv")