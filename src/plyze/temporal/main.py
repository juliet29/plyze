from pathlib import Path
import polars as pl


from plyze.qoi.data.data import select_custom_times, to_dataframe, TimeSelection
from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry as QR

# NOTE: this has a different organziation than rest of data, so may belong in JPGNV or a different repo entirely, depending on how extensive it becomes..


def make_wind_pressure_df(sql: Path, ts: TimeSelection):
    pass


def make_zonal_df(sql: Path, ts: TimeSelection):
    zonal_qois = [QR.temp, QR.vent_vol, QR.mix_vol]
    dfs = [
        to_dataframe(select_custom_times(qoidata=QOIandData(qoi, sql), ts=ts))
        for qoi in zonal_qois
    ]
    join_df = pl.concat(dfs, how="align")
    return join_df


def get_temporal_qois(case_names: list[str], sqls: list[Path]):
    # df_wind = make_wind_pressure_df()
    # zonal_qois = [QR.temp, QR.vent_vol, QR.mix_vol]
    enviro_qois = [QR.site.all]
