from dataclasses import dataclass
from typing import NamedTuple, Sequence, TypeVar
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


# TODO: move to utils4plans
def tuple_to_coord(tup: tuple[float, float]):
    return Coord(x=tup[0], y=tup[1])


def make_parent_paths(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


class GraphPath(NamedTuple):
    object_name: str
    qoi_name: str

    def make_json_path(self, folder_name: str):
        return Path(folder_name) / self.object_name / f"{self.qoi_name}.nc"

    def make_save_path(self, root: Path, folder_name: str):
        return root / self.make_json_path(folder_name)


def make_paths(keys: tuple[str, ...], object_name: str, folder_name: str):
    return {k: GraphPath(object_name, k).make_json_path(folder_name) for k in keys}


class ZoneDataPaths(NamedTuple):
    mix_vol: Path
    vent_vol: Path
    temp: Path


class EdgeDataPaths(NamedTuple):
    flow_in: Path
    flow_out: Path

    # @classmethod
    # def keys(cls):
    #     return list(cls._asdict().keys())


class ExternalNodeDataPaths(NamedTuple):
    external_wind_pressure: Path


_T = TypeVar("_T", EdgeDataPaths, ZoneDataPaths, ExternalNodeDataPaths)


def make_paths2(
    ntup: type[_T],
    object_name: str,
    root: Path,
    folder_name: str,
) -> tuple[_T, _T]:
    values = [
        GraphPath(object_name, k).make_json_path(folder_name) for k in ntup._fields
    ]
    json_paths: _T = ntup(*values)  # type: ignore[call-arg]
    root_paths: _T = ntup(*[root / i for i in json_paths])  # type: ignore[call-arg]
    make_parent_paths(root_paths[0])
    return json_paths, root_paths


@dataclass
class DataWriter:
    root: Path
    folder_name: str

    def write_edge(self, input: Edge):
        name = f"{input.u}__{input.v}"
        json_paths, root_paths = make_paths2(
            EdgeDataPaths, name, self.root, self.folder_name
        )

        input.data.flow_in.to_netcdf(root_paths.flow_in)
        input.data.flow_out.to_netcdf(root_paths.flow_out)

        return json_paths

    def write_external_node(self, input: ExternalNode):
        json_paths, root_paths = make_paths2(
            ExternalNodeDataPaths, input.name, self.root, self.folder_name
        )

        input.data.external_wind_pressure.to_netcdf(root_paths.external_wind_pressure)
        return json_paths

    def write_zone(self, input: ZoneNode):
        json_paths, root_paths = make_paths2(
            ZoneDataPaths, input.name, self.root, self.folder_name
        )

        input.data.ventilation_volume.to_netcdf(root_paths.vent_vol)
        input.data.mixing_volume.to_netcdf(root_paths.mix_vol)
        input.data.temperature.to_netcdf(root_paths.temp)
        return json_paths

        vals = [
            self.root / input.name / i
            for i in ["mixing_volume.nc", "ventilation_volume.nc", "temperature.nc"]
        ]
        paths = ZoneDataPaths(*vals)

        make_parent_paths(paths.vent_vol)
        input.data.ventilation_volume.to_netcdf(paths.vent_vol)
        input.data.mixing_volume.to_netcdf(paths.mix_vol)
        input.data.temperature.to_netcdf(paths.temp)

        return paths


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
    mixing_volume: Path
    ventilation_volume: Path
    temperature: Path


class ZoneNodeModel(BaseModel):
    name: str
    data: ZoneNodeDataModel

    @classmethod
    def from_original(cls, dw: DataWriter, zone: ZoneNode):
        paths = dw.write_zone(zone)
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
                mixing_volume=xr.open_dataarray(self.data.mixing_volume),
                ventilation_volume=xr.open_dataarray(self.data.ventilation_volume),
                temperature=xr.open_dataarray(self.data.temperature),
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
    def write(cls, G: FlowGraph, json_path: Path, data_folder_name: str):
        data_path = json_path.parent / data_folder_name
        dw = DataWriter(data_path)
        zone_nodes = [ZoneNodeModel.from_original(dw, i) for i in G.zone_nodes]
        external_nodes = [
            ExternalNodeModel.from_original(dw, i) for i in G.external_nodes
        ]
        edges = [EdgeModel.from_original(dw, i) for i in G.edges_with_data]

        model = cls.model_validate(
            {"nodes": zone_nodes + external_nodes, "edges": edges}
        )
        write_json(model.model_dump(mode="json"), json_path, OVERWRITE=True)
