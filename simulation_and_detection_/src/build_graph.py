import os
import pandas as pd
import torch
from torch_geometric.data import Data

# Configuration
INPUT_FILE = 'splits/train_clean_numeric.csv'  # Only features, no labels
OUTPUT_FILE = 'splits/train_graph_0.pt'

# Context columns for edge creation (must be among your features)
CONTEXT_COLS = ['masked_user', 'source_ip', 'resource']

def build_graph(df, context_cols):
    # Node features: all columns (features only)
    node_features = df.values
    num_nodes = node_features.shape[0]

    # Build edges: connect nodes sharing any context value
    edge_index = []
    for col in context_cols:
        value_to_indices = df.groupby(col).groups
        for indices in value_to_indices.values():
            indices = list(indices)
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        edge_index.append([indices[i], indices[j]])
                        edge_index.append([indices[j], indices[i]])  # undirected

    if len(edge_index) == 0:
        raise ValueError("No edges created! Check your context columns.")

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    x = torch.tensor(node_features, dtype=torch.float)

    data = Data(x=x, edge_index=edge_index)
    return data

def main():
    df = pd.read_csv(INPUT_FILE)
    print(f"Columns used for node features ({len(df.columns)}): {list(df.columns)}")
    data = build_graph(df, CONTEXT_COLS)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    torch.save(data, OUTPUT_FILE)
    print(f"Graph saved to {OUTPUT_FILE}")
    print(f"Num nodes: {data.num_nodes}, Num edges: {data.num_edges}")
    print(f"Node feature shape: {data.x.shape}")

if __name__ == '__main__':
    main()
