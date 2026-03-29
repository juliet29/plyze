from dataclasses import dataclass
from torch_geometric.data import Dataset
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GCNConv, GAE
from torch_geometric.nn import global_mean_pool
import torch

from plyze.classify.data import GraphDataset


class GCN(torch.nn.Module):
    def __init__(self, hidden_channels, dataset: Dataset):
        super(GCN, self).__init__()
        torch.manual_seed(12345)
        self.conv1 = GCNConv(dataset.num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        # self.lin = Linear(hidden_channels, dataset.num_classes)

    def forward(self, x, edge_index, batch):
        # 1. Obtain node embeddings
        x = self.conv1(x, edge_index)
        x = x.relu()
        x = self.conv2(x, edge_index)
        x = x.relu()
        x = self.conv3(x, edge_index)

        # 2. Readout layer
        x = global_mean_pool(x, batch)  # [batch_size, hidden_channels]
        # number of graphs * length of staxked features; len of columns x..; adjacency matrix will help differentiate..

        # # 3. Apply a final classifier
        # x = F.dropout(x, p=0.5, training=self.training)
        # x = self.lin(x)

        return x


# TODO: could move this to utils
def report_batching(data_loader: DataLoader):
    for step, data in enumerate(data_loader):
        print(f"Step {step + 1}:")
        print("=======")
        print(f"Number of graphs in the current batch: {data.num_graphs}")
        print(data)
        print()


# TODO this should probably all be a class
@dataclass
class GAEPipeline:
    dataset_: GraphDataset
    train_size: int
    batch_size: int
    embedding_size: int
    learning_rate: float

    def prep_data(
        self,
    ):  # TODO: good candidate for post init.. or a helper function.. or part of the dataset function?  / intermediate class? doesn't feel like this belongs here..
        self.dataset = self.dataset_.shuffle()
        self.train_dataset = self.dataset[: self.train_size]
        self.test_dataset = self.dataset[self.train_size :]

        assert isinstance(self.train_dataset, Dataset)
        assert isinstance(self.test_dataset, Dataset)

        self.train_loader = DataLoader(
            self.train_dataset, batch_size=self.batch_size, shuffle=True
        )
        self.test_loader = DataLoader(
            self.test_dataset, batch_size=self.batch_size, shuffle=False
        )

    def prep_model(self):
        assert isinstance(self.dataset, Dataset)
        self.model = GAE(GCN(hidden_channels=self.embedding_size, dataset=self.dataset))
        self.optimizer = torch.optim.Adam(self.model.parameters(), self.learning_rate)

    def train_model(self, x, ix: torch.Tensor):
        self.model.train()
        self.optimizer.zero_grad()
        z = self.model.encode(x, ix)
        loss = self.model.recon_loss(z, ix)
        loss.backward()
        self.optimizer.step()
        return float(loss)

    def test(
        self, x, pos_ix: torch.Tensor, neg_ix: torch.Tensor, train_ix: torch.Tensor
    ):
        self.model.eval()
        with torch.no_grad():
            z = self.model.encode(x, pos_ix)
        return self.model.test(z, pos_ix, neg_ix)


# def run_gae(pipeline: GAEPipeline, epochs: int):
#     for epoch in range(1, epochs + 1):
#         loss = pipeline.train_model()
#         auc, ap = pipeline.test(pipeline.dataset.test_pos_edge_index, data.test_neg_edge_index)
#
#
#
