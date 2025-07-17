import pandas as pd
import json
import os
from feature_extraction import extract_all_features

# ========== Configuration ==========
INPUT_CSV = "benchmark_dataset_sampled.csv"
CACHE_PATH = "semantic_cache.json"
OUT_CSV = "train_features.csv"

# ========== 1. Load Dataset ==========
df = pd.read_csv(INPUT_CSV)
assert 'Password' in df.columns and 'Label' in df.columns, "Input CSV must contain 'Password' and 'Label' columns"
df = df[df['Label'].isin([1, 2, 3, 4])]  # Ensure only valid labels are included

# ========== 2. Load Semantic Cache ==========
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        semantic_cache = json.load(f)
else:
    semantic_cache = {}

# ========== 3. Feature Extraction with Caching ==========
def extract_features_with_cache(password: str) -> dict:
    if password in semantic_cache:
        pii_prob = semantic_cache[password].get('Probability', 0.0)
        feats = extract_all_features(password)
        feats['pii_included_probability'] = pii_prob
    else:
        feats = extract_all_features(password)
        semantic_cache[password] = {
            "Probability": feats.get("pii_included_probability", 0.0)
        }
    return feats

# ========== 4. Process All Records ==========
features_list = []

for idx, row in df.iterrows():
    pw = row['Password']
    label = int(row['Label'])  # Label values expected to be 1/2/3/4
    feats = extract_features_with_cache(pw)
    feats['Password'] = pw
    feats['label'] = label
    features_list.append(feats)

    if (idx + 1) % 10 == 0:
        print(f"[INFO] Processed {idx + 1} samples...")

print(f"[DONE] Feature extraction completed. Total: {len(features_list)} samples")

# ========== 5. Save Cache ==========
with open(CACHE_PATH, "w", encoding="utf-8") as f:
    json.dump(semantic_cache, f, indent=2, ensure_ascii=False)

# ========== 6. Export to CSV ==========
features_df = pd.DataFrame(features_list)
features_df.to_csv(OUT_CSV, index=False)
print(f"[SAVED] Feature CSV written to: {OUT_CSV}")
