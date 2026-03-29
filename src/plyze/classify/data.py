from typing import Callable, Union, Protocol
import torch
from torch_geometric.data import Dataset
from pathlib import Path
import networkx as nx
from torch_geometric.utils import from_networkx


# @dataclass
# class DataHandler:
#     graphs: list[nx.Graph]
#     root: Path
#
#     def make_data(self) -> list[Data]:
#         return [from_networkx(i) for i in self.graphs]
#
#     def make_dataset(self):
#         d = Dataset(
#             root=self.root,
#         )
#
## TODO: put this in a higher level util
class CanIDFtoNetworkX(Protocol):
    def idf_to_graph(
        self, idf: Path
    ) -> (
        nx.Graph
    ):  # TODO: not an actual graph, but something that inherits from it, allowing to have multiple graphs
        ...


class GraphDataset(Dataset):
    # NOTE: this is an interesting inversion of snakemake process.., but will make it works by passing the expected fileneames in and out..
    # TODO: should put data somewhere downloadable, so doesn't depend on scratch..
    # TODO: can we sync to scratch?
    def __init__(
        self,
        idf_transformer: CanIDFtoNetworkX,
        root: Path,
        log: Path,
        transform: Callable,
        pre_filter: Callable,
        pre_transform: Callable,
    ):
        super().__init__(
            root=root._str,
            log=log._str,
            transform=transform,
            pre_filter=pre_filter,
            pre_transform=pre_transform,
        )
        self.idf_transformer = idf_transformer

    @property
    def raw_file_names(self) -> Union[str, list[str], tuple[str, ...]]:
        return super().raw_file_names  # TODO: this should come from snakemake..

    @property
    def processed_file_names(self) -> Union[str, list[str], tuple[str, ...]]:
        return super().processed_file_names  # TODO: this should come from snakemake..

    def process(self):
        def process_file(path: Path):
            file_name = ""  # TODO!, this should be coming from snakemake also..
            graph = self.idf_transformer.idf_to_graph(
                path
            )  # TODO: can also be a callable.., this might make more sense than a protocol..
            # TODO: there will be another step here maybe where actually get the networkx graph?
            data = from_networkx(graph)
            torch.save(data, file_name)

        [process_file(Path(i)) for i in self.raw_paths]

    # def get(self):
    #     pass
