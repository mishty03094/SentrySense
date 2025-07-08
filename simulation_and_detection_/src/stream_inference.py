import os
import json
import pandas as pd
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import numpy as np
from datetime import datetime
import pytz

# Paths
GRAPH_PATH = 'splits/train_graph_0.pt'
MODEL_PATH = 'models/gnn_model.pt'
TRAIN_PROCESSED = 'splits/train_clean_numeric.csv'
STREAM_FILE = 'splits/stream_clean_numeric.csv'
LOG_FILE = 'logs/stream_logs.jsonl'

CONTEXT_COLS = ['masked_user', 'source_ip', 'resource']
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Mapping from encoded location to city name and timezone
location_code_to_city = {
    -1: "Unknown",   # Unseen/unknown
    0: "London",
    1: "Tokyo",
    2: "New York",
    3: "Berlin",
    4: "São Paulo"
}
city_to_timezone = {
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "New York": "America/New_York",
    "Berlin": "Europe/Berlin",
    "São Paulo": "America/Sao_Paulo"
}

class GNNEncoder(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)
        self.relu = torch.nn.ReLU()
    def forward(self, x, edge_index):
        x = self.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return x

class GNNAutoEncoder(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.encoder = GNNEncoder(in_channels, hidden_channels, out_channels)
        self.decoder = torch.nn.Linear(out_channels, in_channels)
    def forward(self, x, edge_index):
        z = self.encoder(x, edge_index)
        x_hat = self.decoder(z)
        return x_hat

def add_node_to_graph(data, node_features, df_existing, context_cols, stream_row_idx):
    x_new = torch.cat([data.x, node_features.unsqueeze(0)], dim=0)
    num_nodes = x_new.shape[0]
    edge_index = [list(edge) for edge in data.edge_index.t().tolist()]
    found_connection = False
    for col in context_cols:
        val = int(df_existing.iloc[stream_row_idx][col])
        matching_indices = df_existing.index[df_existing[col] == val].tolist()
        for idx in matching_indices:
            found_connection = True
            edge_index.append([idx, num_nodes - 1])
            edge_index.append([num_nodes - 1, idx])
    if not found_connection:
        edge_index.append([num_nodes - 1, num_nodes - 1])
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    return Data(x=x_new, edge_index=edge_index)

def get_local_hour(location_code):
    city = location_code_to_city.get(location_code, "Unknown")
    if city == "Unknown" or city not in city_to_timezone:
        return None, city
    tz = pytz.timezone(city_to_timezone[city])
    local_time = datetime.now(tz)
    return local_time.hour, city

def main():
    # Load graph and model
    data = torch.load(GRAPH_PATH, weights_only=False)
    df_existing = pd.read_csv(TRAIN_PROCESSED)
    in_channels = data.x.size(1)
    hidden_channels = 64
    out_channels = 32

    model = GNNAutoEncoder(in_channels, hidden_channels, out_channels)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.eval()
    model.to(DEVICE)

    # --- Load and align streaming data ---
    train_df = pd.read_csv(TRAIN_PROCESSED)
    stream_df = pd.read_csv(STREAM_FILE)

    # Align columns: keep only those in train, in the same order
    stream_df_aligned = stream_df[[col for col in train_df.columns if col in stream_df.columns]]
    for col in train_df.columns:
        if col not in stream_df_aligned.columns:
            stream_df_aligned[col] = 0
    stream_df_aligned = stream_df_aligned[train_df.columns]
    stream_df_aligned.to_csv(STREAM_FILE, index=False)

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Only process the first row (simulate 1-row streaming)
    if len(stream_df_aligned) == 0:
        print("No events left in stream.")
        return
    row = stream_df_aligned.iloc[0]
    node_features = torch.tensor(row.values, dtype=torch.float)

    log_entry = {
        "stream_index": int(df_existing.shape[0]),
        "raw_features": row.to_dict()
    }

    # --- Real-time location-based time anomaly check ---
    location_code = int(row['location'])
    local_hour, city = get_local_hour(location_code)
    if local_hour is not None and 0 <= local_hour < 4:
        log_entry.update({
            "anomaly": "medium",
            "reason": f"Local time in {city} is {local_hour}:00 — time is not good (12am-4am)"
        })
        print(f"Medium anomaly: Local time in {city} is {local_hour}:00 — time is not good (12am-4am). Skipping model inference.")
    else:
        assert data.x.shape[1] == node_features.shape[0] == 32, (
            f"Feature mismatch: graph has {data.x.shape[1]}, node has {node_features.shape[0]}"
        )
        temp_graph = add_node_to_graph(data, node_features, df_existing, CONTEXT_COLS, 0)
        temp_graph = temp_graph.to(DEVICE)

        with torch.no_grad():
            x_hat = model(temp_graph.x, temp_graph.edge_index)
        recon_error = torch.nn.functional.mse_loss(
            x_hat[-1], temp_graph.x[-1], reduction='sum'
        ).item()

        threshold = 10000000  # Example: adjust as needed for your data
        is_anomaly = recon_error > threshold

        log_entry.update({
            "anomaly": is_anomaly,
            "score": recon_error
        })

        if is_anomaly:
            # --- Explainability: Top 2 features by absolute error (human-readable) ---
            original = temp_graph.x[-1].cpu().numpy()
            reconstructed = x_hat[-1].cpu().numpy()
            abs_errors = np.abs(original - reconstructed)
            feature_names = list(row.index)
            top_indices = abs_errors.argsort()[-2:][::-1]

            explanation = []
            for idx in top_indices:
                feat = feature_names[idx]
                orig_val = original[idx]
                recon_val = reconstructed[idx]
                if abs(orig_val - recon_val) > 0:
                    reason = f"The attribute '{feat}' is unusual: expected around {recon_val:.2f}, but got {orig_val:.2f}."
                else:
                    reason = f"The attribute '{feat}' shows a normal value."
                explanation.append(reason)
            log_entry["why"] = explanation

            print(f"Event {df_existing.shape[0]}: score={recon_error:.4f} [ANOMALY]")
            print("Top contributing features to anomaly score:")
            for reason in explanation:
                print(f"  {reason}")
        else:
            print(f"Event {df_existing.shape[0]}: score={recon_error:.4f} [normal]")

    # --- Append to log ---
    with open(LOG_FILE, 'a') as log_f:
        log_f.write(json.dumps(log_entry) + '\n')

    # --- Cyclic streaming: append this row to end of stream and update file ---
    stream_df_aligned = stream_df_aligned.iloc[1:]
    stream_df_aligned = pd.concat([stream_df_aligned, row.to_frame().T], ignore_index=True)
    stream_df_aligned.to_csv(STREAM_FILE, index=False)

if __name__ == '__main__':
    main()
