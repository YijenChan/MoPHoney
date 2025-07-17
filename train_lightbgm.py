import pandas as pd
import lightgbm as lgb
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score

# ========== Configuration ==========
INPUT_CSV = "train_features.csv"
MODEL_OUTPUT = "router_model.txt"
TEST_RATIO = 0.3
RANDOM_SEED = 42

# ========== 1. Load Dataset ==========
df = pd.read_csv(INPUT_CSV)

# ========== 2. Split Features and Labels ==========
X = df.drop(columns=["label", "Password"], errors="ignore")
y = df["label"]

# ========== 3. Train/Validation Split ==========
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=TEST_RATIO, stratify=y, random_state=RANDOM_SEED
)

# ========== 4. Construct LightGBM Dataset ==========
train_data = lgb.Dataset(X_train, label=y_train)
val_data = lgb.Dataset(X_val, label=y_val)

# ========== 5. Model Parameters ==========
NUM_CLASS = y.nunique()
params = {
    'objective': 'multiclass',
    'num_class': NUM_CLASS,
    'metric': 'multi_logloss',
    'learning_rate': 0.1,
    'num_leaves': 31,
    'verbose': -1
}

# ========== 6. Train the Model ==========
print(f"🚀 Training LightGBM router model (num_class = {NUM_CLASS})...")
model = lgb.train(
    params,
    train_data,
    valid_sets=[train_data, val_data],
    num_boost_round=100,
    callbacks=[
        lgb.early_stopping(stopping_rounds=10),
        lgb.log_evaluation(period=10)
    ]
)

# ========== 7. Save the Model ==========
model.save_model(MODEL_OUTPUT)
print(f"✅ Model saved to: {MODEL_OUTPUT}")

# ========== 8. Evaluation Report ==========
y_pred_proba = model.predict(X_val)
y_pred = y_pred_proba.argmax(axis=1)

print("\n📊 Classification Report on Validation Set:")
print(classification_report(y_val, y_pred, digits=4))

acc = accuracy_score(y_val, y_pred)
macro_f1 = f1_score(y_val, y_pred, average='macro')

print(f"\n🎯 Accuracy       : {acc:.4f}")
print(f"🎯 Macro-F1 Score : {macro_f1:.4f}")
