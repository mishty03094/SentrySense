import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GATConv
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import kneighbors_graph

class AnomalyDetector(nn.Module):
    def __init__(self, num_features, hidden_dim=24):
        super().__init__()
        self.conv1 = GATConv(num_features, hidden_dim, heads=2, dropout=0.6)
        self.conv2 = GATConv(hidden_dim*2, hidden_dim, heads=2, dropout=0.6)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim*2, hidden_dim),
            nn.ELU(),
            nn.Dropout(0.6),
            nn.Linear(hidden_dim, 2)
        )
    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.elu(self.conv1(x, edge_index))
        x = F.elu(self.conv2(x, edge_index))
        return self.classifier(x)


def feature_engineering(logs):
    features = []
    encoders = {
        'user': LabelEncoder(),
        'action': LabelEncoder(),
        'location': LabelEncoder(),
        'role': LabelEncoder()
    }
    encoders['user'].fit([log['user'] for log in logs])
    encoders['action'].fit([log['action'] for log in logs])
    encoders['location'].fit([log['location'] for log in logs])
    encoders['role'].fit([log['role'] for log in logs])
    for log in logs:
        hour = int(log['time'].split('T')[1].split(':')[0])
        features.append([
            encoders['user'].transform([log['user']])[0],
            encoders['action'].transform([log['action']])[0],
            encoders['location'].transform([log['location']])[0],
            encoders['role'].transform([log['role']])[0],
            hour,
            log['risk_score'],
            int("admin" in log['role'] and "deleted" in log['action']),
            int(log['location'] in ['RU', 'UA'])
        ])
    return np.array(features), encoders

def build_graph(features, k=7):
    adj_matrix = kneighbors_graph(features, k, mode='connectivity', include_self=True)
    edge_index = np.array(adj_matrix.nonzero())
    return torch.tensor(edge_index, dtype=torch.long)

def main():
    with open("logs/sample_logs.json") as f:
        logs = json.load(f)
    features, encoders = feature_engineering(logs)
    labels = np.array([log['is_anomaly'] for log in logs])
    scaler = StandardScaler()
    features = scaler.fit_transform(features)
    edge_index = build_graph(features, k=7)
    indices = np.arange(len(labels))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, stratify=labels, random_state=42
    )
    train_idx, val_idx = train_test_split(
        train_idx, test_size=0.25, stratify=labels[train_idx], random_state=42
    )
    train_mask = torch.zeros(len(labels), dtype=torch.bool)
    val_mask = torch.zeros(len(labels), dtype=torch.bool)
    test_mask = torch.zeros(len(labels), dtype=torch.bool)
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True
    data = Data(
        x=torch.tensor(features, dtype=torch.float),
        edge_index=edge_index,
        y=torch.tensor(labels, dtype=torch.long),
        train_mask=train_mask,
        val_mask=val_mask,
        test_mask=test_mask
    )
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AnomalyDetector(num_features=features.shape[1]).to(device)
    data = data.to(device)
    anomaly_weight = len(labels) / sum(labels) if sum(labels) > 0 else 1.0
    class_weights = torch.tensor([1.0, anomaly_weight], dtype=torch.float).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=2e-4)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='max', 
        patience=8, 
        factor=0.5
    )
    best_f1 = 0
    best_thresh = 0.5
    patience_counter = 0
    for epoch in range(50):
        model.train()
        optimizer.zero_grad()
        out = model(data)
        loss = criterion(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        optimizer.step()
        model.eval()
        with torch.no_grad():
            val_out = model(data)
            val_probs = F.softmax(val_out[data.val_mask], dim=1)[:, 1].cpu().numpy()
            val_labels = data.y[data.val_mask].cpu().numpy()
            best_f1_val = 0
            current_best_thresh = 0.5
            for thresh in np.linspace(0.1, 0.9, 17):
                preds = (val_probs > thresh).astype(int)
                _, _, f1, _ = precision_recall_fscore_support(val_labels, preds, average='binary')
                if f1 > best_f1_val:
                    best_f1_val = f1
                    current_best_thresh = thresh
            scheduler.step(best_f1_val)
            if best_f1_val > best_f1:
                best_f1 = best_f1_val
                best_thresh = current_best_thresh
                patience_counter = 0
                torch.save(model.state_dict(), 'best_model.pt')
                print(f"Epoch {epoch}: New best F1={best_f1_val:.4f} at threshold={best_thresh:.2f}")
            else:
                patience_counter += 1
                if patience_counter > 10:
                    print("Early stopping triggered.")
                    break
    model.load_state_dict(torch.load('best_model.pt'))
    model.eval()
    with torch.no_grad():
        test_out = model(data)
        test_probs = F.softmax(test_out[data.test_mask], dim=1)[:, 1].cpu().numpy()
        test_labels = data.y[data.test_mask].cpu().numpy()
        test_preds = (test_probs > best_thresh).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(test_labels, test_preds, average='binary')
        auc = roc_auc_score(test_labels, test_probs)
        accuracy = accuracy_score(test_labels, test_preds)
        print("\n=== Final Test Performance ===")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")
        print(f"Optimal Threshold: {best_thresh:.4f}")
    with torch.no_grad():
        all_out = model(data)
        all_probs = F.softmax(all_out, dim=1)[:, 1].cpu().numpy()
        all_preds = (all_probs > best_thresh).astype(int)
        anomalies = [log for i, log in enumerate(logs) if all_preds[i] == 1]
        with open("detected_anomalies.json", "w") as f:
            json.dump(anomalies, f, indent=2)
        print(f"\nDetected {len(anomalies)} anomalies")

if __name__ == "__main__":
    main()
