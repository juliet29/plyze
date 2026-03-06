from dataclasses import dataclass
from pathlib import Path
import networkx as nx
from utils4plans.io import read_json, write_json
from utils4plans.lists import get_unique_one
from pydantic import BaseModel

from plan2eplus.geometry.coords import (
    Coord,
)  # TODO: make plan2eplus use utils4plans coords, just using here because that is what the incoming graph will use...

# TODO: but do have some ability to control how this is read in.. when get to actually handlling io for the AFNGraph..
#


@dataclass
class JPNodeData:
    is_carrier: bool = False
    level: int = 0
    coord: Coord = Coord(0, 0)
    ix_on_level: int = 0


@dataclass
class JPNode(BaseModel):
    name: str
    data: JPNodeData

    @property
    def entry(self):
        return (self.name, {"data": self.data})


class Edge(BaseModel):
    # TODO: include this in utils4plans, since all models for graphs involving IO will extend this
    source: str
    target: str

    @property
    def as_tuple(self):
        return (self.source, self.target)


class JPGraph(nx.Graph):
    # TODO: init function that takes jpnodes and their edges..

    def add_jpnodes(self, nodes: list[JPNode]):
        self.add_nodes_from([i.entry for i in nodes])

    @classmethod
    def create(cls, nodes: list[JPNode], edges: list[Edge]):
        c = cls()
        c.add_jpnodes(nodes)
        c.add_edges_from([i.as_tuple for i in edges])
        pass

    @property
    def num_nodes(self):
        return len(self)

    @property
    def jpnodes(self):
        nodes = self.nodes(data=True)
        res = [JPNode(name=i, data=data_["data"]) for i, data_ in nodes]
        return res

    def update_jpnode(self, name: str, data: JPNodeData):
        # TODO: test
        nx.set_node_attributes(G=self, values={"data": data}, name=name)

    def get_jpnode_by_name(self, name: str):
        node = get_unique_one(self.jpnodes, lambda node: node.name == name)
        return node

    def show(self):
        levels = set([i.data.level for i in self.jpnodes])
        s = "\n"
        for level in levels:
            if level >= 0:
                nodes = [i.name for i in self.jpnodes if i.data.level == level]
                info = f"{level}: {",".join(nodes)}\n"
                s += info
        return s


class JPGraphModel(BaseModel):
    nodes: list[JPNode]
    edges: list[Edge]

    def read(self, path: Path):
        data = read_json(
            path,
        )
        model_graph = self.model_validate(data)
        return JPGraph.create(model_graph.nodes, model_graph.edges)

    def write(self, path: Path):
        write_json(self.model_dump(), path, OVERWRITE=True)


class JPGMetrics(BaseModel):
    total_depth: float
    mean_depth: float
    relative_asymmetry: float
    control_value: dict[str, float]

    def write(self, path: Path):
        write_json(self.model_dump(), path, OVERWRITE=True)

    @classmethod
    def read(cls, path: Path):
        pass
        # TODO need to read for creating the unifying data...
