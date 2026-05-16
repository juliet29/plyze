from pathlib import Path
from typing import Callable, NamedTuple, Generic, ParamSpec, TypeVar
import xarray as xr
from dataclasses import dataclass, field

from plyze.qoi.registries.interfaces import GenericQOI
from plyze.utils import XArrayNames


P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True)
class GraphQOI(GenericQOI, Generic[P, R]):
    fx: Callable[P, R] = field(
        default=lambda x: xr.DataArray
    )  # pyright: ignore[reportAssignmentType]


class GraphQOIAndData(NamedTuple):
    graph_qoi: GraphQOI
    value: xr.DataArray


class GraphQOIHolder:
    holder_dict: dict[str, xr.DataArray] = {}

    def update(self, graph_qoi: GraphQOI, value: xr.DataArray):
        self.holder_dict[graph_qoi.nickname] = value

    def write(self, path: Path):
        pass

    @classmethod
    def read(cls, path: Path):
        pass


@dataclass
class GraphQOIBaseCalculator:
    holder: GraphQOIHolder
    name: str
    """Name of the zone or the plan that this data will cover"""

    def register(self, graph_qoi: GraphQOI, value: xr.DataArray):
        try:
            value[XArrayNames.SPACE] = self.name
        except ValueError as e:
            raise Exception(f"Could not set name for {graph_qoi.name} -> {e}")
        # logger.info(f"Updated xarray space name {value.space_names}")
        self.holder.update(graph_qoi, value)

    def calculate(self, functions: list[Callable]):
        for f in functions:
            f()

    def run(self) -> None: ...

    def __call__(self):
        self.run()
