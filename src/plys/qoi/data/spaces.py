from dataclasses import dataclass
import polars as pl
from pathlib import Path
from plan2eplus.ezcase.ez import EZ
from plan2eplus.ops.subsurfaces.ezobject import Subsurface, SubsurfaceType
from plan2eplus.ops.zones.ezobject import Zone
from plan2eplus.results.collections import SpaceTypesLiteral
from utils4plans.lists import get_unique_one


@dataclass
class BasicSpaceData:
    idf_name: str
    display_name: str
    space_type: SpaceTypesLiteral


@dataclass
class BasicZoneData(BasicSpaceData):
    area: float


@dataclass
class BasicSurfaceData(BasicSpaceData):
    type_: SubsurfaceType
    direction: str
    zone_display_name: str
    area: float


def upper_idf_column(df: pl.DataFrame):
    return df.with_columns(space_names=pl.col("idf_name").str.to_uppercase())


def create_space_df(idf_path: Path):
    # TODO: enable passing in a graph so can look at centrality..
    case = EZ(idf_path)

    def make_zone(zone: Zone):
        return BasicZoneData(zone.zone_name, zone.room_name, "Zone", zone.domain.area)

    def make_subsurface(s: Subsurface):
        zone_name = s.surface.zone_name
        zone = get_unique_one(case.objects.zones, lambda x: x.zone_name == zone_name)
        return BasicSurfaceData(
            s.subsurface_name,
            s.display_name,
            "Surface",
            s.subsurface_type,
            s.surface.direction.name,
            zone.room_name,
            zone.domain.area,
        )

    zones = [make_zone(i) for i in case.objects.zones]
    subsurfaces = [make_subsurface(i) for i in case.objects.subsurfaces]
    zdf = pl.DataFrame(zones).pipe(upper_idf_column)
    sdf = pl.DataFrame(subsurfaces).pipe(upper_idf_column)
    df = pl.concat([zdf, sdf], how="diagonal")
    return df
