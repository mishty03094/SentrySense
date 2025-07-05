import torch
import torch.nn as nn
import torch.optim as optim
from torch_geometric.nn import GCNConv
import os

GRAPH_PATH = 'splits/train_graph_0.pt'
MODEL_PATH = 'models/gnn_model.pt'
EPOCHS = 50
LR = 1e-3
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

class GNNEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)
        self.relu = nn.ReLU()
    def forward(self, x, edge_index):
        x = self.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return x

class GNNAutoEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.encoder = GNNEncoder(in_channels, hidden_channels, out_channels)
        self.decoder = nn.Linear(out_channels, in_channels)
    def forward(self, x, edge_index):
        z = self.encoder(x, edge_index)
        x_hat = self.decoder(z)
        return x_hat

def train(model, data, epochs, lr, device):
    model = model.to(device)
    data = data.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        x_hat = model(data.x, data.edge_index)
        loss = criterion(x_hat, data.x)
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch}/{epochs} | Loss: {loss.item():.6f}")
    return model

def main():
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    data = torch.load(GRAPH_PATH, weights_only=False)
    in_channels = data.x.size(1)  # This will be 32
    hidden_channels = 64
    out_channels = 32
    model = GNNAutoEncoder(in_channels, hidden_channels, out_channels)
    model = train(model, data, EPOCHS, LR, DEVICE)
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"Trained model saved to {MODEL_PATH}")

if __name__ == '__main__':
    main()
