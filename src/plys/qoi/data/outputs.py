from pathlib import Path
from typing import NamedTuple
from loguru import logger
import polars as pl
from plys.qoi.data.data import to_multi_data
from plys.qoi.data.interfaces import CaseQOIandData
from plys.qoi.registries.main import QOIRegistry as QR


class StandardData(NamedTuple):
    zonal: pl.DataFrame
    surface: pl.DataFrame


def get_zonal_qois(idf: Path, sql: Path):
    qois = [
        QR.temp,
        QR.vent_vol,
        QR.vent_heat_gain,
        QR.vent_heat_loss,
        QR.custom.net_vent_heat_gain,
        QR.mix_vol,
        QR.mix_heat_gain,
        QR.mix_heat_loss,
        QR.custom.net_mix_heat_gain,
        QR.custom.combined_volume,
        # TODO: latent heat gain (which is not even in output variable requests currently), net incoming flow over a zone, net outgoing flow over a zone, combined mixing heat loss and heat gain
    ]
    return to_multi_data(qois, idf, sql)


def get_surface_qois(idf: Path, sql: Path):
    qois = [QR.flow_out, QR.flow_in, QR.custom.net_out_flow]
    return to_multi_data(qois, idf, sql)


# TODO: environmental qois
# NOTE: environmental qois would only need to be recorded once, and can actually be taken directly from the EPW, which is a different process


def gather_standard_data(
    idf: Path,
    sql: Path,
):

    zonal_df = get_zonal_qois(idf, sql)
    surface_df = get_surface_qois(idf, sql)
    return StandardData(zonal_df, surface_df)


def consolidate_data(case_datas: list[CaseQOIandData]):
    # assuming these are of all the same "type" of dataframe, ie zonal qois, or surface_qois, etc..
    logger.debug(case_datas[0].dataframe.shape)

    df = pl.concat(
        [i.dataframe.with_columns(case_name=pl.lit(i.case_name)) for i in case_datas]
    )
    expected_num_rows = sum(
        [i.dataframe["space_names"].unique().len() for i in case_datas]
        * case_datas[0].dataframe["datetimes"].unique().len()
    )
    assert df.height == expected_num_rows
    return df
