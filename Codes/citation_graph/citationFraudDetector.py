import torch.nn as nn
from torch_geometric.nn import GCNConv, global_mean_pool

# Graph Neural Network
class CitationFraudDetector(nn.Module):
  def __init__(self, in_channels, hidden_channels):
    super().__init__()
    self.conv1 = GCNConv(in_channels, hidden_channels)
    self.conv2 = GCNConv(hidden_channels, hidden_channels)
    self.lin = nn.Linear(hidden_channels, 2)

  def forward(self, x, edge_index, batch):
    x = self.conv1(x, edge_index).relu()
    x = self.conv2(x, edge_index).relu()
    x = global_mean_pool(x, batch)
    x = self.lin(x)
    return x