import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os

# --- CONFIGURATION ---
ORIGINAL_FILE = 'data/Access-Log-Anomaly-Detection-Dataset.csv'
OUT_FILE = 'splits/test_labeled_clean_numeric.csv'
os.makedirs('splits', exist_ok=True)

cols_to_remove = ['timestamp', 'anomaly_score', 'anomaly_bin']
categorical_cols = [
    'masked_user', 'source_ip', 'destination_ip', 'action', 'resource', 'protocol',
    'access_result', 'location', 'device_type', 'day_of_week', 'month',
    'source_subnet', 'dest_subnet', 'resource_category'
]

df = pd.read_csv(ORIGINAL_FILE)
df = df.drop(columns=[col for col in cols_to_remove if col in df.columns], errors='ignore')

label_encoders = {}
for col in categorical_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

for col in df.columns:
    if col != 'target':
        df[col] = pd.to_numeric(df[col], errors='raise')

df.to_csv(OUT_FILE, index=False)
print(f"Saved cleaned and encoded test file: {OUT_FILE}")
