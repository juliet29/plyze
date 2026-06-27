from dataclasses import dataclass
from typing import Any, Hashable, Literal, NamedTuple, Sequence, TypeVar

import networkx as nx
import xarray as xr
from plan2eplus.geometry.coords import Coord
from plan2eplus.ops.subsurfaces.ezobject import SubsurfaceType
from utils4plans.sets import set_equality

from plyze.qoi.xarray_helpers import get_data
from plyze.utils import XArrayNames

ZoneNodeQOINames = Literal[
    "mixing_volume",
    "ventilation_volume",
    "temperature",
    "zone_inflow",
    "zone_outflow",
    "zone_dimless_flow",
    "zone_dimless_temp",
]


class AmbientData(NamedTuple):
    t_out: xr.DataArray
    wind_speed: xr.DataArray
    wind_direction: xr.DataArray

    # def to_dataset(self):
    #     d = {k: v for k,v in self._asdict().items()}
    #     return xr.Dataset()
    #


class ZoneComputedData(NamedTuple):
    zone_inflow: xr.DataArray
    zone_outflow: xr.DataArray
    zone_dimless_flow: xr.DataArray
    zone_dimless_temp: xr.DataArray


@dataclass
class ZoneNodeData:
    location: Coord
    area: float
    aspect_ratio: float
    is_in_afn: bool
    mixing_volume: xr.DataArray
    ventilation_volume: xr.DataArray
    temperature: xr.DataArray
    computed_data: ZoneComputedData | None = None

    @property
    def idf_name(self):
        return get_data(self.temperature[XArrayNames.SPACE])

    def get_qoi_array(self, name: ZoneNodeQOINames):
        try:
            val = self.__dict__[name]
        except KeyError:
            assert self.computed_data
            val = self.computed_data._asdict()[name]
        assert isinstance(val, xr.DataArray)
        return val

    def update_computed_data(self, data: ZoneComputedData):
        self.computed_data = data


class ExternalNodeData(NamedTuple):
    location: Coord
    external_wind_pressure: xr.DataArray


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
    surface_area: float
    surface_type: SubsurfaceType | Literal["Airboundary"]


class Edge(NamedTuple):
    u: str
    v: str
    data: EdgeData

    def __hash__(self) -> int:
        return hash(frozenset((self.u, self.v)))

    def __eq__(self, other: Any):
        if isinstance(other, Edge):
            return self.u == other.u and self.v == other.v
        elif isinstance(other, tuple):
            assert len(other) == 2
            return set_equality([self.u, self.v], other)
        raise ValueError(f"{other} does not have an appropriate type!")

    @property
    def entry(self):
        return (self.u, self.v, {"data": self.data})


FlowNodeType = TypeVar("FlowNodeType", bound=FlowNode)


class FlowGraph(nx.Graph):
    def add_flow_nodes(self, nodes: list[FlowNodeType]):
        self.add_nodes_from([i.entry for i in nodes])

    def add_flow_edges(self, edges: list[Edge]):
        self.add_edges_from([i.entry for i in edges])

    @classmethod
    def create(
        cls,
        nodes: list[FlowNodeType],
        edges: list[Edge],
    ):
        G = cls()
        G.add_flow_nodes(nodes)
        G.add_flow_edges(edges)
        return G

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

    def get_edges_of_zone(self, zone: ZoneNode):
        e = self.edges(zone.name)
        return [i for i in e]
