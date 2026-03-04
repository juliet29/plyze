from dataclasses import dataclass
import networkx as nx
from utils4plans.lists import get_unique_one

from plan2eplus.geometry.coords import (
    Coord,
)  # TODO: make plan2eplus use utils4plans coords, just using here because that is what the incoming graph will use...

# TODO: but do have some ability to control how this is read in.. when get to actually handlling io for the AFNGraph..


@dataclass
class JPNodeData:
    is_carrier: bool = False
    level: int = 0
    coord: Coord = Coord(0, 0)
    ix_on_level: int = 0


@dataclass
class JPNode:
    name: str
    data: JPNodeData

    @property
    def entry(self):
        return (self.name, {"data": self.data})


class JPGraph(nx.Graph):
    # TODO: init function that takes jpnodes and their edges..
    def add_jpnodes(self, nodes: list[JPNode]):
        self.add_nodes_from([i.entry for i in nodes])

    @property
    def num_nodes(self):
        return len(self)

    @property
    def jpnodes(self):
        # NOTE: THIS SHOULD BE READ ONLY -> by virtue of being a propety it is read-only
        nodes = self.nodes(data=True)
        res = [JPNode(name=i, data=data_["data"]) for i, data_ in nodes]
        return res

    def update_jpnode(self, name: str, data: JPNodeData):
        # TODO: test
        nx.set_node_attributes(G=self, values={"data": data}, name=name)
        # res = [JPNode(i, data["data"]) for i, data in nodes]
        # return res
        #

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
