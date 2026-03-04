from dataclasses import dataclass
from functools import partial
from typing import Callable, Literal, NamedTuple
from plan2eplus.results.collections import SpaceTypesLiteral
from utils4plans.lists import sort_and_group_objects
import xarray as xr
from pathlib import Path
from plan2eplus.results.sql import get_qoi
from plan2eplus.ops.output.interfaces import OutputVariables
import re


@dataclass(frozen=True)
class GenericQOI:
    name: str
    nickname: str
    unit: str
    space_type: SpaceTypesLiteral

    @property
    def label(self):
        return f"{self.name} [{self.unit}]"

    def update_xarray(self, arr: xr.DataArray):
        arr.name = self.name
        arr.attrs["units"] = self.unit
        # TODO would be good to relate to the info that Ladybug gives..


class CustomQOIComponents(NamedTuple):
    a: OutputVariables
    b: OutputVariables
    c: OutputVariables | None = None
    d: OutputVariables | None = None
    e: OutputVariables | None = None


def default_custom_qoi_fx(
    components: CustomQOIComponents, operation: Literal["+", "-"], sql_path: Path
) -> xr.DataArray:
    arr_a = get_qoi(components.a, sql_path).data_arr
    arr_b = get_qoi(components.b, sql_path).data_arr

    if operation == "-":
        return arr_a - arr_b
    elif operation == "+":
        return arr_a + arr_b


# @dataclass(frozen=True)
# class OutgoingFlow(GenericQOI):
#     name: str
#
#     def fx(self, sql_path: Path):
#         # arr_a = get_qoi(self.components.a, sql_path).data_arr
#         # need to combine all outgoing flows for a zone and change space names to be zones..
#         # so here would need the space idfs...
#         # this could potentially alter the dag...
#         pass


# OTHER FUNCTIONS --- > Modifying the xarray dataarray in some more complex way...
#
def find_drn(space_name: str):
    pattern = re.compile("(NORTH)|(SOUTH)|(EAST)|(WEST)")
    res = pattern.search(space_name.upper())
    if res:
        return res.group()
    else:
        raise ValueError(
            f"External node name {space_name} does not contain a direction!"
        )


def get_wind_pressure_unique_external_nodes(sql_path: Path):
    wind_pressure = get_qoi("AFN Node Wind Pressure", sql_path).data_arr

    grouped_space_names = sort_and_group_objects(
        wind_pressure.space_names.to_series().to_list(), lambda x: find_drn(x)
    )
    # just want the first from each node
    selected_space_names = [i[0] for i in grouped_space_names]
    # TODO: good opportunity to simplify the names..  to be the direction..
    return wind_pressure.sel(space_names=selected_space_names)


@dataclass(frozen=True)
class CustomQOI(GenericQOI):
    name: str
    components: CustomQOIComponents | None = None
    operation: Literal["+", "-"] = "-"
    fx: Callable[[Path], xr.DataArray] | None = None

    def __post_init__(self):
        if not self.fx:
            assert self.components
            assert self.operation
            f = partial(default_custom_qoi_fx, self.components, self.operation)
            object.__setattr__(self, "fx", f)


class CustomQOIRegistry:
    net_flow = CustomQOI(  # NOTE: this is really more of a dissipation metric..
        name="AFN Linkage Node 1 to Node 2 Net Flow Rate ",
        components=CustomQOIComponents(
            "AFN Linkage Node 1 to Node 2 Volume Flow Rate",
            "AFN Linkage Node 2 to Node 1 Volume Flow Rate",
        ),
        nickname="net_flow",
        unit="m3/s",
        space_type="Surface",
    )
    combined_volume = CustomQOI(
        name="AFN Combined Mixing and Ventilation Volume",
        components=CustomQOIComponents(
            "AFN Zone Mixing Volume",
            "AFN Zone Ventilation Volume",
        ),
        operation="+",
        nickname="combined_volume",
        unit="m3",
        space_type="Zone",
    )
    net_vent_heat_gain = CustomQOI(
        name="AFN Zone Ventilation Net Sensible Heat Gain Rate",
        components=CustomQOIComponents(
            "AFN Zone Ventilation Sensible Heat Gain Rate",
            "AFN Zone Ventilation Sensible Heat Loss Rate",
        ),
        nickname="net_vent_heat_gain",
        unit="W",
        space_type="Zone",
    )
    net_mix_heat_gain = CustomQOI(
        name="AFN Zone Mixing Net Sensible Heat Gain Rate",
        components=CustomQOIComponents(
            "AFN Zone Mixing Sensible Heat Gain Rate",
            "AFN Zone Mixing Sensible Heat Loss Rate",
        ),
        nickname="net_mix_heat_gain",
        unit="W",
        space_type="Zone",
    )
    unique_wind_pressure = CustomQOI(
        name="AFN Facade External Node Wind Pressure",
        nickname="unique_wind_pressure",
        unit="Pa",
        space_type="System",
        fx=get_wind_pressure_unique_external_nodes,
    )
