from pathlib import Path
from typing import Callable, NamedTuple, Generic, ParamSpec, TypeVar
import xarray as xr
from dataclasses import dataclass, field

from plyze.qoi.registries.interfaces import GenericQOI


def zone_inflow(node_1_2_flow: list[xr.DataArray]) -> xr.DataArray:
    # TODO: assert that all have the same vals..
    # dt = [i.]
    return sum(node_1_2_flow)  # pyright: ignore[reportReturnType]


def zone_outflow(node_2_1_flow: list[xr.DataArray]) -> xr.DataArray:
    # TODO: check that the nodes are aligned!
    return sum(node_2_1_flow)  # pyright: ignore[reportReturnType]


def zone_dimless_flow(
    wind_speed: xr.DataArray, zone_sum_flow: xr.DataArray, surface_areas: list[float]
):
    sum_areas = sum(surface_areas)
    return zone_sum_flow / (sum_areas * wind_speed)


def zone_dimless_temp(t_out: xr.DataArray, zone_t: xr.DataArray):
    return zone_t / t_out


P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True)
class GraphQOI(GenericQOI, Generic[P, R]):
    fx: Callable[P, R] = field(
        default=lambda x: xr.DataArray
    )  # pyright: ignore[reportAssignmentType]


class GraphQOIRegistry:
    zone_inflow = GraphQOI(
        "zone_inflow",
        "zone_inflow",
        unit="m3/s",
        space_type="Zone",
        fx=zone_inflow,
    )
    zone_outflow = GraphQOI(
        "zone_outflow", "zone_outflow", unit="m3/s", space_type="Zone", fx=zone_outflow
    )

    zone_dimless_flow = GraphQOI(
        "zone_dimless_flow",
        "zone_dimless_flow",
        unit="",
        space_type="Zone",
        fx=zone_dimless_flow,
    )

    zone_dimless_temp = GraphQOI(
        "zone_dimless_temp",
        "zone_dimless_temp",
        unit="",
        space_type="Zone",
        fx=zone_dimless_temp,
    )


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

    def register(self, graph_qoi: GraphQOI, value: xr.DataArray):
        self.holder.update(graph_qoi, value)

    def calculate(self, functions: list[Callable]):
        for f in functions:
            f()

    def run(self) -> None: ...

    def __call__(self):
        self.run()

    # zone_inflow: xr.DataArray
    # zone_outflow: xr.DataArray
