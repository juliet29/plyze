from typing import Hashable, Literal, NamedTuple, Sequence, TypeVar
from dataclasses import dataclass

import networkx as nx
import xarray as xr
from plan2eplus.geometry.coords import Coord

NodeType = Literal["zone", "external_node"]  # TODO: this may be a bit redundant..


class ZoneNodeData(NamedTuple):
    type_: NodeType
    location: Coord
    area: float
    aspect_ratio: float
    is_in_afn: bool


class ExternalNodeData(NamedTuple):
    type_: NodeType
    location: Coord
    external_wind_pressure: xr.DataArray
    is_dominant_external_node: bool


@dataclass(frozen=True)
class FlowNode:
    name: str
    data: ExternalNodeData | ZoneNodeData

    @property
    def entry(self):
        return (self.name, {"data": self.data})


@dataclass(frozen=True)
class ZoneNode(FlowNode):
    name: str
    data: ZoneNodeData


@dataclass(frozen=True)
class ExternalNode(FlowNode):
    name: str
    data: ExternalNodeData


class EdgeData(NamedTuple):
    flow_in: xr.DataArray
    flow_out: xr.DataArray


class Edge(NamedTuple):
    u: str
    v: str
    data: EdgeData

    @property
    def entry(self):
        return (self.u, self.v, {"data": self.data})


FlowNodeType = TypeVar("FlowNodeType", bound=FlowNode)


class FlowGraph(nx.Graph):
    def add_flow_nodes(self, nodes: list[FlowNodeType]):
        self.add_nodes_from([i.entry for i in nodes])

    def add_flow_edges(self, edges: list[Edge]):
        self.add_edges_from([i.entry for i in edges])

    @property
    def edges_with_data(self):
        edges = [Edge(u, v, data["data"]) for u, v, data in self.edges(data=True)]
        return edges

    @property
    def zone_nodes(self):
        nodes = self.nodes(data=True)
        res = [
            ZoneNode(i, data["data"])
            for i, data in nodes
            if isinstance(data["data"], ZoneNodeData)
        ]
        return res

    @property
    def external_nodes(self) -> list[ExternalNode]:
        nodes = self.nodes(data=True)
        res = [
            ExternalNode(i, data["data"])
            for i, data in nodes
            if isinstance(data["data"], ExternalNodeData)
        ]
        return res

    @property
    def zone_names(self):
        return [i.name for i in self.zone_nodes]

    @property
    def external_node_names(self):
        return [i.name for i in self.external_nodes]

    @property
    def all_names(self):
        return self.nodes(data=False)

    @property
    def all_nodes(self):
        return self.zone_nodes + self.external_nodes

    @property
    def layout(self) -> dict[Hashable, tuple[float, float] | Sequence[float]]:
        return {node.name: list(node.data.location.as_tuple) for node in self.all_nodes}

    @property
    def zone_only_subgraph(self):
        sg = nx.Graph()
        sg.add_nodes_from(self.zone_names)
        return sg

    @property
    def external_node_only_subgraph(self):
        sg = nx.Graph()
        sg.add_nodes_from(self.external_node_names)
        return sg
