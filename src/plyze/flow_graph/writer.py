from dataclasses import dataclass
from typing import NamedTuple, TypeVar
from pathlib import Path

from loguru import logger

from plyze.flow_graph.interfaces import (
    Edge,
    ExternalNode,
    ZoneNode,
)


def make_parent_paths(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


class GraphPath(NamedTuple):
    object_name: str
    qoi_name: str

    def make_json_path(self, folder_name: str):
        return Path(folder_name) / self.object_name / f"{self.qoi_name}.nc"

    # def make_save_path(self, root: Path, folder_name: str):
    #     res = root / self.make_json_path(folder_name)
    #     logger.debug(res)
    #     return res
    #


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
    logger.debug(root_paths)
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
