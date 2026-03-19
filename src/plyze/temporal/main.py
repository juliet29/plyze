from pathlib import Path
from typing import Sequence
import polars as pl


from plyze.qoi.data.data import select_custom_times, to_dataframe, TimeSelection
from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.interfaces import QOIType
from plyze.qoi.registries.main import QOIRegistry as QR
from plyze.qoi.xarray_helpers import find_drn_in_name

# NOTE: this has a different organziation than rest of data, so may belong in JPGNV or a different repo entirely, depending on how extensive it becomes..
#


# NOTE:, for time selectio want ALL the times..

schema = pl.Schema(
    {
        "datetimes": pl.Datetime(time_unit="us", time_zone=None),
        "NORTH": pl.Float64,
        "SOUTH": pl.Float64,
        "WEST": pl.Float64,
        "max unique_wind_pressure": pl.Float64,
        "DRN of max unique_wind_pressure": pl.String,
        "temp": pl.Float64,
        "vent_vol": pl.Float64,
        "mix_vol": pl.Float64,
        "case_name": pl.String,
        "t_out": pl.Float64,
        "wind_speed": pl.Float64,
        "wind_direction": pl.Float64,
    }
)


def get_dataframe(qoi: QOIType, sql: Path, time_selection: TimeSelection):
    return to_dataframe(
        select_custom_times(qoidata=QOIandData(qoi, sql), ts=time_selection)
    )


def make_multiqoi_df(qois: Sequence[QOIType], sql: Path, ts: TimeSelection):
    dfs = [get_dataframe(qoi, sql, ts) for qoi in qois]
    join_df = pl.concat(dfs, how="align")
    return join_df


def make_wind_pressure_df(sql: Path, ts: TimeSelection):
    # NOTE: not taking the absolute value here...
    DRN = "direction"
    wp = QR.custom.unique_wind_pressure
    df = get_dataframe(wp, sql, ts).with_columns(
        pl.col("space_names")
        .map_elements(find_drn_in_name, return_dtype=pl.String)
        .alias(DRN)
    )

    df_pivot = df.pivot(on=DRN, index="datetimes", values=wp.nickname)

    df_max = df.group_by("datetimes").agg(
        pl.col(wp.nickname).max().alias(f"max {wp.nickname}"),
        pl.col(DRN).max_by(wp.nickname).alias(f"DRN of max {wp.nickname}"),
    )
    return df_pivot.join(df_max, on="datetimes")


def get_temporal_qois(case_names: list[str], sqls: list[Path], ts: TimeSelection):

    def make_case_df(case_name, sql):
        try:
            wind_df = make_wind_pressure_df(sql, ts)
            zonal_df = (
                make_multiqoi_df(zonal_qois, sql, ts)
                .group_by("datetimes")
                .agg([pl.mean(i.nickname) for i in zonal_qois])
            )
            return wind_df.join(zonal_df, on="datetimes").with_columns(
                case_name=pl.lit(case_name)
            )
        except:
            return None

    # this could potentially be a part of the registry like the environmenal variables
    zonal_qois = [
        QR.temp,
        QR.vent_vol,
        QR.mix_vol,
    ]

    dfs = [make_case_df(case, sql) for case, sql in zip(case_names, sqls)]
    filter_dfs = [i for i in dfs if i is not None]
    case_df = pl.concat(filter_dfs, how="vertical")

    enviro_df = make_multiqoi_df(QR.site.all, sqls[0], ts).drop("space_names")

    join_df = case_df.join(enviro_df, on="datetimes")
    assert join_df.schema == schema
    return join_df


# TODO share the schema of the final df!
