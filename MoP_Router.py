import pandas as pd
import lightgbm as lgb
from feature_extraction import extract_all_features
import numpy as np

# ========== Configuration ==========
MODEL_PATH = "router_model.txt"

# ========== 1. Load the Pretrained LightGBM Model ==========
model = lgb.Booster(model_file=MODEL_PATH)

# ========== 2. Inference Function ==========
def get_password_class_prob(password: str) -> list:
    """
    Given a password string, return the classification probability distribution
    used for MoP-Mixer routing.
    """
    features = extract_all_features(password)
    df = pd.DataFrame([features])
    prob = model.predict(df)  # Shape: [1, num_classes]
    return prob[0]

# ========== 3. Test Example ==========
if __name__ == "__main__":
    sample_passwords = [
        "abc123",
        "lb1990401",
        "QwErTy!123",
    ]

    print("🔍 Password Classification Probabilities:")
    for pw in sample_passwords:
        probs = get_password_class_prob(pw)
        probs_str = ", ".join(f"{p:.4f}" for p in probs)
        print(f"🔐 {pw} → [ {probs_str} ]")
