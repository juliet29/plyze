from pathlib import Path
from loguru import logger
import networkx as nx
from utils4plans.io import read_json, write_json
from utils4plans.lists import get_unique_one
from pydantic import BaseModel


# TODO: but do have some ability to control how this is read in.. when get to actually handlling io for the AFNGraph..
#


# @dataclass
class JPNodeData(BaseModel):
    is_carrier: bool = False
    level: int = 0
    # coord: Coord = Coord(0, 0)
    # ix_on_level: int = 0
    #


# @dataclass
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
    graph_name: str = ""
    # TODO: init function that takes jpnodes and their edges..

    def add_jpnodes(self, nodes: list[JPNode]):
        self.add_nodes_from([i.entry for i in nodes])

    @classmethod
    def create(
        cls, name: str, nodes: list[JPNode], edges: list[Edge] | list[tuple[str, str]]
    ):
        G = cls()
        G.graph_name = name
        G.add_jpnodes(nodes)
        if isinstance(edges[0], Edge):
            # TODO: figure out how to assert for a group of edges
            G.add_edges_from(
                [
                    i.as_tuple  # pyright: ignore[reportAttributeAccessIssue]
                    for i in edges  # pyright: ignore[reportAttributeAccessIssue]
                ]
            )
        else:
            G.add_edges_from(edges)  # pyright: ignore[reportArgumentType]
        return G

    @property
    def num_nodes(self):
        return len(self)

    @property
    def jpnodes(self):
        nodes = self.nodes(data=True)
        res = [JPNode(name=i, data=data_["data"]) for i, data_ in nodes]
        return res

    @property
    def jpedges(self):
        edges = self.edges(data=False)
        res = [Edge(source=u, target=v) for u, v in edges]
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
    graph_name: str
    nodes: list[JPNode]
    edges: list[Edge]

    @classmethod
    def read(cls, path: Path):
        data = read_json(path)
        model = cls.model_validate(data)
        logger.debug(data)

        logger.debug(model)
        G = JPGraph.create(model.graph_name, model.nodes, model.edges)
        return G

    @classmethod
    def write(cls, G: JPGraph, path: Path):
        model = cls.model_validate(
            {"graph_name": G.graph_name, "nodes": G.jpnodes, "edges": G.jpedges}
        )
        write_json(model.model_dump(), path, OVERWRITE=True)


class JPGMetrics(BaseModel):
    graph_name: str
    total_depth: float
    mean_depth: float
    relative_asymmetry: float
    # control_value: dict[str, float]

    @classmethod
    def read(cls, path: Path):
        data = read_json(path)
        model = cls.model_validate(data)
        return model

    def write(self, path: Path):
        write_json(self.model_dump(), path, OVERWRITE=True)

        # TODO need to read for creating the unifying data...
