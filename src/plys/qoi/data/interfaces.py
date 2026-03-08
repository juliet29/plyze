from dataclasses import dataclass
import polars as pl
import xarray as xr
from pathlib import Path
from plan2eplus.results.sql import get_qoi
from plys.qoi.registries.interfaces import EpQOI, CustomQOI, QOIType


@dataclass
class QOIandData:
    qoi: QOIType
    sql_path: Path
    arr: xr.DataArray | None = None
    dataframe: pl.DataFrame | None = None

    @property
    def original_arr(self):
        if isinstance(self.qoi, EpQOI):
            qoi_res = get_qoi(self.qoi.name, self.sql_path)
            # TODO: introduce some leniency for system variables.
            # assert (
            #     qoi_res.space_type == self.qoi.space_type
            # ), f"Expected space type is {qoi_res.space_type}, but plan2eplus space type is {self.qoi.space_type}"
            assert (
                qoi_res.unit == self.qoi.unit
            ), f"Expected unit for {self.qoi.name} is {qoi_res.unit}, but plan2eplus  unit is {self.qoi.unit}"
            return qoi_res.data_arr

        elif isinstance(self.qoi, CustomQOI):
            # TODO: may have a mapping? but can just change the fx attribute.. don't need a mapping..
            assert self.qoi.fx
            return self.qoi.fx(self.sql_path)
        raise ValueError(
            f"Can't compute arr unless type of self.qoi is CompQOI or EpQOI. Instead, type of variable {self.qoi.name} is {type(self.qoi)}"
        )

    def set_array(self, arr: xr.DataArray):
        self.arr = arr

    def set_dataframe(self, df: pl.DataFrame):
        self.dataframe = df
