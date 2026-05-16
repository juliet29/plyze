from typing import Literal, Sequence
from plan2eplus.ops.subsurfaces.ezobject import SubsurfaceType
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
    ZoneComputedData,
    ZoneNode,
    ZoneNodeData,
)
from plyze.flow_graph.writer import DataWriter


# TODO: move to utils4plans
def tuple_to_coord(tup: tuple[float, float]):
    return Coord(x=tup[0], y=tup[1])


def open_xarray(root_path: Path, path: Path):
    return xr.open_dataarray(root_path / path)


class ExternalNodeDataModel(BaseModel):
    location: tuple[float, float]
    external_wind_pressure: Path


class ExternalNodeModel(BaseModel):
    name: str
    data: ExternalNodeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, node: ExternalNode):
        paths = dw.write_external_node(node)
        return cls(
            name=node.name,
            data=ExternalNodeDataModel(
                location=node.data.location.as_tuple,
                external_wind_pressure=paths.external_wind_pressure,
            ),
        )

    def to_original(self, root_path: Path) -> ExternalNode:
        return ExternalNode(
            name=self.name,
            data=ExternalNodeData(
                location=tuple_to_coord(self.data.location),
                external_wind_pressure=open_xarray(
                    root_path, self.data.external_wind_pressure
                ),
            ),
        )


class ZoneComputedDataModel(BaseModel):
    zone_inflow: Path
    zone_outflow: Path
    zone_dimless_flow: Path
    zone_dimless_temp: Path


class ZoneNodeDataModel(BaseModel):
    location: Coord
    area: float
    aspect_ratio: float
    is_in_afn: bool
    mixing_volume: Path
    ventilation_volume: Path
    temperature: Path
    computed_data: ZoneComputedDataModel


class ZoneNodeModel(BaseModel):
    name: str
    data: ZoneNodeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, zone: ZoneNode):
        paths = dw.write_zone(zone)
        computed_paths = dw.write_computed_zone(zone)
        return cls(
            name=zone.name,
            data=ZoneNodeDataModel(
                location=zone.data.location,
                area=zone.data.area,
                aspect_ratio=zone.data.aspect_ratio,
                is_in_afn=zone.data.is_in_afn,
                mixing_volume=paths.mix_vol,
                ventilation_volume=paths.vent_vol,
                temperature=paths.temp,
                computed_data=ZoneComputedDataModel(
                    zone_inflow=computed_paths.zone_inflow,
                    zone_outflow=computed_paths.zone_outflow,
                    zone_dimless_flow=computed_paths.zone_dimless_flow,
                    zone_dimless_temp=computed_paths.zone_dimless_temp,
                ),
            ),
        )

    def to_original(self, root_path: Path) -> ZoneNode:
        computed_data = ZoneComputedData(
            zone_inflow=open_xarray(root_path, self.data.computed_data.zone_inflow),
            zone_outflow=open_xarray(root_path, self.data.computed_data.zone_outflow),
            zone_dimless_flow=open_xarray(
                root_path, self.data.computed_data.zone_dimless_flow
            ),
            zone_dimless_temp=open_xarray(
                root_path, self.data.computed_data.zone_dimless_temp
            ),
        )
        return ZoneNode(
            name=self.name,
            data=ZoneNodeData(
                location=self.data.location,
                area=self.data.area,
                aspect_ratio=self.data.aspect_ratio,
                is_in_afn=self.data.is_in_afn,
                mixing_volume=open_xarray(root_path, self.data.mixing_volume),
                ventilation_volume=open_xarray(root_path, self.data.ventilation_volume),
                temperature=open_xarray(root_path, self.data.temperature),
                computed_data=computed_data,
            ),
        )


class EdgeDataModel(BaseModel):
    flow_in: Path
    flow_out: Path
    surface_area: float
    surface_type: SubsurfaceType | Literal["Airboundary"]


class EdgeModel(BaseModel):
    u: str
    v: str
    data: EdgeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, edge: Edge):
        paths = dw.write_edge(edge)
        return cls(
            u=edge.u,
            v=edge.v,
            data=EdgeDataModel(
                flow_in=paths.flow_in,
                flow_out=paths.flow_out,
                surface_area=edge.data.surface_area,
                surface_type=edge.data.surface_type,
            ),
        )

    def to_original(self, root_path: Path) -> Edge:
        return Edge(
            u=self.u,
            v=self.v,
            data=EdgeData(
                flow_in=open_xarray(root_path, self.data.flow_in),
                flow_out=open_xarray(root_path, self.data.flow_out),
                surface_area=self.data.surface_area,
                surface_type=self.data.surface_type,
            ),
        )


class FlowGraphModel(BaseModel):
    nodes: Sequence[ExternalNodeModel | ZoneNodeModel]
    edges: list[EdgeModel]

    @classmethod
    def read(cls, path: Path):
        data = read_json(path)
        root = path.parent
        model = cls.model_validate(data)
        nodes = [i.to_original(root) for i in model.nodes]
        edges = [i.to_original(root) for i in model.edges]
        G = FlowGraph.create(nodes, edges)
        # TODO: this shouldnt depend on an outside sql file
        return G

    @classmethod
    def write(cls, G: FlowGraph, json_path: Path, data_folder_name: str):
        # TODO: think about how will write the ambient data, if want to write that..
        # or should a path to the sql file be stored?
        dw = DataWriter(json_path.parent, data_folder_name)

        zone_nodes = [ZoneNodeModel.from_original(dw, i) for i in G.zone_nodes]
        external_nodes = [
            ExternalNodeModel.from_original(dw, i) for i in G.external_nodes
        ]
        edges = [EdgeModel.from_original(dw, i) for i in G.edges_with_data]

        model = cls.model_validate(
            {"nodes": zone_nodes + external_nodes, "edges": edges}
        )
        write_json(model.model_dump(mode="json"), json_path, OVERWRITE=True)
