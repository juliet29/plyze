from dataclasses import dataclass
from typing import Literal
import xarray as xr
from pathlib import Path
from plan2eplus.results.sql import get_qoi

from functools import partial
from typing import Callable, NamedTuple
from plan2eplus.results.collections import SpaceTypesLiteral
from plan2eplus.ops.output.interfaces import OutputVariables


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
        # TODO: dont think are using the units on the actual xarray...


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


@dataclass(frozen=True)
class EpQOI(GenericQOI):
    name: OutputVariables


QOIType = CustomQOI | EpQOI
