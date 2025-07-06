import pandas as pd
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import torch.nn.functional as F
import os
import json

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

# Paths
GRAPH_PATH = 'splits/train_graph_0.pt'
MODEL_PATH = 'models/gnn_model.pt'
TRAIN_PROCESSED = 'splits/train_clean_numeric.csv'
TEST_FILE = 'splits/test_labeled_clean_numeric.csv'
LOG_NORMAL = 'logs/normal_events.jsonl'
LOG_ANOMALOUS = 'logs/anomalous_events.jsonl'

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

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

# Load test data
stream_df = pd.read_csv(TEST_FILE)

# Clean target column for robust matching if present
if 'target' in stream_df.columns:
    stream_df['target'] = stream_df['target'].astype(str).str.strip().str.lower()
    print('Unique target values:', stream_df['target'].unique())

# Align columns with train, keep 'target' if present
columns_to_keep = [col for col in df_existing.columns if col in stream_df.columns]
if 'target' in stream_df.columns:
    columns_to_keep.append('target')
stream_df_aligned = stream_df[columns_to_keep]

# Prepare logs
os.makedirs(os.path.dirname(LOG_NORMAL), exist_ok=True)
os.makedirs(os.path.dirname(LOG_ANOMALOUS), exist_ok=True)
normal_log = open(LOG_NORMAL, 'w')
anomalous_log = open(LOG_ANOMALOUS, 'w')

reconstruction_errors_normal = []
reconstruction_errors_anomalous = []

# Identify numeric columns for model input (exclude 'target' and all non-numeric columns)
numeric_columns = [col for col in df_existing.columns if pd.api.types.is_numeric_dtype(df_existing[col])]

for idx, row in stream_df_aligned.iterrows():
    # Only use numeric model input columns for node_features
    node_features = torch.tensor(row[numeric_columns].astype(float).values, dtype=torch.float)
    temp_graph = add_node_to_graph(data, node_features, df_existing, ['masked_user', 'source_ip', 'resource'], 0)
    temp_graph = temp_graph.to(DEVICE)
    with torch.no_grad():
        x_hat = model(temp_graph.x, temp_graph.edge_index)
    recon_error = F.mse_loss(x_hat[-1], temp_graph.x[-1], reduction='sum').item()

    log_entry = {
        'index': int(idx),
        'reconstruction_error': recon_error,
        'features': row.to_dict()
    }

    label = row['target'] if 'target' in row else None
    if label == 'malicious':
        anomalous_log.write(json.dumps(log_entry) + '\n')
        reconstruction_errors_anomalous.append(recon_error)
    else:
        normal_log.write(json.dumps(log_entry) + '\n')
        reconstruction_errors_normal.append(recon_error)

normal_log.close()
anomalous_log.close()

# Calculate threshold
if reconstruction_errors_normal and reconstruction_errors_anomalous:
    normal_max = max(reconstruction_errors_normal)
    anomalous_min = min(reconstruction_errors_anomalous)
    threshold_calculated = (normal_max + anomalous_min) / 2
    print(f"Max reconstruction error for normal: {normal_max}")
    print(f"Min reconstruction error for anomalous: {anomalous_min}")
    print(f"Suggested threshold: {threshold_calculated}")
else:
    threshold_calculated = None
    print("Insufficient data to calculate threshold.")

# Return threshold
print(f"Threshold: {threshold_calculated}")
