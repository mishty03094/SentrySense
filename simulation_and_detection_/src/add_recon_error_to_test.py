import torch
import pandas as pd
import numpy as np
from torch_geometric.nn import GCNConv

# --- Model Definitions ---
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

# --- Paths ---
GRAPH_PATH = 'splits/train_graph_0.pt'
MODEL_PATH = 'models/gnn_model.pt'
TEST_FILE = 'splits/test_labeled_clean_numeric.csv'
OUT_FILE = 'splits/test_labeled_clean_numeric_with_errors.csv'

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# --- Load graph and model ---
data = torch.load(GRAPH_PATH, weights_only=False)
in_channels = data.x.size(1)
hidden_channels = 64
out_channels = 32

model = GNNAutoEncoder(in_channels, hidden_channels, out_channels)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
model.eval()
model.to(DEVICE)

# --- Load test data and prepare features ---
df_test = pd.read_csv(TEST_FILE)
feature_cols = [col for col in df_test.columns if col != 'target']
features = torch.tensor(df_test[feature_cols].values, dtype=torch.float).to(DEVICE)

# --- Compute reconstruction errors ---
with torch.no_grad():
    x_hat = model(features, data.edge_index.to(DEVICE))
    errors = torch.nn.functional.mse_loss(x_hat, features, reduction='none')
    node_errors = errors.sum(dim=1).cpu().numpy()

df_test['recon_error'] = node_errors
df_test.to_csv(OUT_FILE, index=False)
print(f"Saved: {OUT_FILE}")
