import pandas as pd
import os

# Paths
DATA_PATH = "data/Access-Log-Anomaly-Detection-Dataset.csv"
SPLITS_DIR = "splits"
os.makedirs(SPLITS_DIR, exist_ok=True)

TRAIN_FILE = os.path.join(SPLITS_DIR, "train.csv")
TEST_LABELED_FILE = os.path.join(SPLITS_DIR, "test_labeled.csv")
STREAM_FILE = os.path.join(SPLITS_DIR, "stream.csv")

# Columns to remove for model/graph/stream
cols_to_remove = ['anomaly_score', 'target', 'anomaly_bin', 'timestamp']

# 1. Split data (example: 70% train, 30% test/stream)
df = pd.read_csv(DATA_PATH)
train_df = df[df['target'] == 'benign'].sample(frac=0.7, random_state=42)
test_df = df.drop(train_df.index).copy()

# 2. Save train (features only, no labels or timestamp)
train_clean = train_df.drop(columns=[col for col in cols_to_remove if col in train_df.columns], errors='ignore')
train_clean.to_csv(TRAIN_FILE, index=False)

# 3. Save test with labels (for evaluation)
test_df.to_csv(TEST_LABELED_FILE, index=False)

# 4. Save stream (features only, no labels or timestamp)
stream_clean = test_df.drop(columns=[col for col in cols_to_remove if col in test_df.columns], errors='ignore')
stream_clean.to_csv(STREAM_FILE, index=False)
