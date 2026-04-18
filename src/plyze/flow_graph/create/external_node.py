from datetime import datetime
from pathlib import Path
from plan2eplus.ezcase.ez import EZ
import xarray as xr
from plan2eplus.geometry.contact_points import (
    CardinalPoints,
    calculate_cardinal_points,
)
from plyze.flow_graph.interfaces import (
    ExternalNodeData,
    ExternalNode,
)

from plan2eplus.visuals.domains import calculate_cardinal_domain
from plan2eplus.ops.zones.ezobject import Zone

from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.xarray_helpers import find_drn_in_name, select_time


def make_afn_nodes_from_external_nodes(
    direction: str, wind_pressure_data: xr.DataArray, cardinal_locations: CardinalPoints
):
    return ExternalNode(
        direction,
        data=ExternalNodeData(
            type_="external_node",
            location=cardinal_locations[
                direction
            ],  # pyright: ignore[reportArgumentType]
            external_wind_pressure=wind_pressure_data,
            is_dominant_external_node=False,
        ),
    )


def calculate_cardinal_locations(zones: list[Zone], cardinal_expansion_factor):
    cardinal_locations = calculate_cardinal_points(
        calculate_cardinal_domain(
            [i.domain for i in zones],
            cardinal_expansion_factor=cardinal_expansion_factor,
        )
    )
    return cardinal_locations


def make_external_nodes(
    case: EZ,
    sql_path: Path,
    cardinal_expansion_factor: float,
    dt: list[datetime] = [],
):
    cardinal_locations = calculate_cardinal_locations(
        case.objects.zones, cardinal_expansion_factor
    )

    wind_pressure = QOIandData(
        QOIRegistry.custom.unique_wind_pressure, sql_path
    ).original_arr

    if dt:
        wind_pressure = select_time(wind_pressure, dt)

    direction_and_data = [
        (find_drn_in_name(name.item()), data)
        for name, data in wind_pressure.groupby("space_names")
    ]

    external_nodes = [
        make_afn_nodes_from_external_nodes(*i, cardinal_locations)
        for i in direction_and_data
    ]

    return external_nodes
