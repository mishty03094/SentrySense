import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder

SPLITS_DIR = "splits"
TRAIN_FILE = os.path.join(SPLITS_DIR, "train.csv")
STREAM_FILE = os.path.join(SPLITS_DIR, "stream.csv")
TEST_LABELED_FILE = os.path.join(SPLITS_DIR, "test_labeled.csv")  # Evaluation file

TRAIN_OUT = os.path.join(SPLITS_DIR, "train_clean_numeric.csv")
STREAM_OUT = os.path.join(SPLITS_DIR, "stream_clean_numeric.csv")
# Do NOT overwrite test_labeled.csv!

cols_to_remove = ['timestamp', 'anomaly_score', 'target', 'anomaly_bin']

categorical_cols = [
    'masked_user', 'source_ip', 'destination_ip', 'action', 'resource', 'protocol',
    'access_result', 'location', 'device_type', 'day_of_week', 'month',
    'source_subnet', 'dest_subnet', 'resource_category'
]

def safe_label_encode(series, le):
    classes = set(le.classes_)
    return series.map(lambda x: le.transform([x])[0] if x in classes else -1)

def clean_and_encode(input_path, output_path, label_encoders=None, fit=True, align_cols=None):
    df = pd.read_csv(input_path)
    df = df.drop(columns=[col for col in cols_to_remove if col in df.columns], errors='ignore')
    if label_encoders is None:
        label_encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
            else:
                le = label_encoders[col]
                df[col] = safe_label_encode(df[col].astype(str), le)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='raise')
    if align_cols is not None:
        for col in align_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[align_cols]
    df.to_csv(output_path, index=False)
    print(f"Cleaned and encoded file saved to {output_path} (columns: {len(df.columns)})")
    return df, label_encoders

def main():
    train_clean, label_encoders = clean_and_encode(TRAIN_FILE, TRAIN_OUT, fit=True)
    stream_clean, _ = clean_and_encode(STREAM_FILE, STREAM_OUT, label_encoders, fit=False, align_cols=train_clean.columns)
    # Do NOT clean or overwrite test_labeled.csv!
    print("\nPreprocessing complete. All specified columns removed from train/stream, categorical columns encoded, unseen categories in stream marked as -1, and splits aligned.")

if __name__ == "__main__":
    main()
