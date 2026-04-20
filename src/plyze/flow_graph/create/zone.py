from pathlib import Path
from datetime import datetime
from typing import NamedTuple

from polars import datetime
import xarray as xr
from plyze.flow_graph.interfaces import (
    ZoneNodeData,
    ZoneNode,
)

from plan2eplus.ezcase.ez import EZ
from plan2eplus.ops.zones.ezobject import Zone


from plan2eplus.geometry.domain import Domain
from plan2eplus.geometry.ortho_domain import OrthoDomain

from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.xarray_helpers import get_data_by_space_name, select_time


def calculate_domain_aspect_ratio(
    domain: OrthoDomain | Domain,
):  # TODO: implement on the class, especially OrthoDomain, and clean up duplication!
    if isinstance(domain, Domain):
        return domain.horz_range.size / domain.vert_range.size
    return (
        domain.bounding_domain.horz_range.size / domain.bounding_domain.vert_range.size
    )


def make_zone_from_node(
    zone: Zone,
    mixing_volume: xr.DataArray,
    ventilation_volume: xr.DataArray,
    temperature: xr.DataArray,
):
    domain = zone.domain
    zone_name = zone.zone_name
    # TODO: determine if room is in AFN.. but skip this metric for now..

    return ZoneNode(
        zone.room_name,
        data=ZoneNodeData(
            location=domain.centroid,
            area=domain.area,
            aspect_ratio=calculate_domain_aspect_ratio(domain),
            is_in_afn=False,
            mixing_volume=get_data_by_space_name(mixing_volume, zone_name),
            ventilation_volume=get_data_by_space_name(ventilation_volume, zone_name),
            temperature=get_data_by_space_name(temperature, zone_name),
            # vent_volume=get_space_arr(ventilation_volume, zone_name),
            # mix_volume=get_space_arr(mixing_volume, zone_name),
            # ach=get_space_arr(ach, zone_name),
        ),
    )


class ZoneDataArray(NamedTuple):
    mix_vol: xr.DataArray
    vent_vol: xr.DataArray
    temp: xr.DataArray


def make_zones_for_graph(case: EZ, sql: Path, dt: list[datetime]):
    zone_nodes = case.objects.zones
    arr = [
        QOIandData(i, sql).original_arr
        for i in [QOIRegistry.mix_vol, QOIRegistry.vent_vol, QOIRegistry.temp]
    ]

    arr2 = []
    if dt:
        for i in arr:
            i = select_time(i, dt)
            arr2.append(i)

        zones = [make_zone_from_node(i, *arr2) for i in zone_nodes]
        return zones

    zones = [make_zone_from_node(i, *arr) for i in zone_nodes]
    return zones
