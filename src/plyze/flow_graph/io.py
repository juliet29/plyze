from dataclasses import dataclass
from typing import Sequence
import xarray as xr
from plan2eplus.geometry.coords import Coord
from pydantic import BaseModel
from pathlib import Path
from utils4plans.io import read_json, write_json

from plyze.flow_graph.interfaces import (
    Edge,
    EdgeData,
    ExternalNode,
    ExternalNodeData,
    FlowGraph,
    ZoneNode,
    ZoneNodeData,
)


def tuple_to_coord(tup: tuple[float, float]):
    return Coord(x=tup[0], y=tup[1])


@dataclass
class DataWriter:
    root: Path

    def write_edge(self, input: Edge):
        name = f"{input.u}__{input.v}"
        flow_in_path = self.root / name / "flow_in"
        flow_out_path = self.root / name / "flow_out"

        input.data.flow_in.to_netcdf(flow_in_path)
        input.data.flow_out.to_netcdf(flow_out_path)

        return flow_in_path, flow_out_path

    def write_external_node(self, input: ExternalNode):
        path = self.root / input.name / "external_wind_pressure"

        input.data.external_wind_pressure.to_netcdf(path)

        return path


class ExternalNodeDataModel(BaseModel):
    location: tuple[float, float]
    external_wind_pressure: Path


class ExternalNodeModel(BaseModel):
    name: str
    data: ExternalNodeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, node: ExternalNode):
        path = dw.write_external_node(node)
        return cls(
            name=node.name,
            data=ExternalNodeDataModel(
                location=node.data.location.as_tuple, external_wind_pressure=path
            ),
        )

    def to_original(self) -> ExternalNode:
        return ExternalNode(
            name=self.name,
            data=ExternalNodeData(
                location=tuple_to_coord(self.data.location),
                external_wind_pressure=xr.open_dataarray(
                    self.data.external_wind_pressure
                ),
            ),
        )


class ZoneNodeDataModel(BaseModel):
    location: Coord
    area: float
    aspect_ratio: float
    is_in_afn: bool


class ZoneNodeModel(BaseModel):
    name: str
    data: ZoneNodeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, zone: ZoneNode):
        return cls(
            name=zone.name,
            data=ZoneNodeDataModel(
                location=zone.data.location,
                area=zone.data.area,
                aspect_ratio=zone.data.aspect_ratio,
                is_in_afn=zone.data.is_in_afn,
            ),
        )

    def to_original(self) -> ZoneNode:
        return ZoneNode(
            name=self.name,
            data=ZoneNodeData(
                location=self.data.location,
                area=self.data.area,
                aspect_ratio=self.data.aspect_ratio,
                is_in_afn=self.data.is_in_afn,
            ),
        )


class EdgeDataModel(BaseModel):
    flow_in: Path
    flow_out: Path


class EdgeModel(BaseModel):
    u: str
    v: str
    data: EdgeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, edge: Edge):
        flow_in, flow_out = dw.write_edge(edge)
        return cls(
            u=edge.u,
            v=edge.v,
            data=EdgeDataModel(
                flow_in=flow_in,
                flow_out=flow_out,
            ),
        )

    def to_original(self) -> Edge:
        return Edge(
            u=self.u,
            v=self.v,
            data=EdgeData(
                flow_in=xr.open_dataarray(self.data.flow_in),
                flow_out=xr.open_dataarray(self.data.flow_out),
            ),
        )


class FlowGraphModel(BaseModel):
    nodes: Sequence[ExternalNodeModel | ZoneNodeModel]
    edges: list[EdgeModel]

    @classmethod
    def read(cls, path: Path):
        data = read_json(path)
        model = cls.model_validate(data)
        nodes = [i.to_original() for i in model.nodes]
        edges = [i.to_original() for i in model.edges]
        G = FlowGraph.create(nodes, edges)
        return G

    @classmethod
    def write(cls, G: FlowGraph, path: Path):
        dw = DataWriter(path)
        zone_nodes = [ZoneNodeModel.from_original(dw, i) for i in G.zone_nodes]
        external_nodes = [
            ExternalNodeModel.from_original(dw, i) for i in G.external_nodes
        ]
        edges = [EdgeModel.from_original(dw, i) for i in G.edges_with_data]

        model = cls.model_validate(
            {"nodes": zone_nodes + external_nodes, "edges": edges}
        )
        write_json(model.model_dump(), path, OVERWRITE=True)
