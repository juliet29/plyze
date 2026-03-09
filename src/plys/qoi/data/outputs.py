from pathlib import Path
import polars as pl
from typing import NamedTuple
from plys.qoi.data.data import to_multi_data
from plys.qoi.registries.main import QOIRegistry as QR


class StandardData(NamedTuple):
    zonal: pl.DataFrame
    surface: pl.DataFrame


def get_zonal_qois(idf: Path, sql: Path, case_name: str):
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
    return to_multi_data(qois, idf, sql, case_name)


def get_surface_qois(idf: Path, sql: Path, case_name: str):
    qois = [QR.flow_12, QR.flow_21, QR.custom.net_flow]
    return to_multi_data(qois, idf, sql, case_name)


# TODO: environmental qois
#
#
def gather_standard_data(idf: Path, sql: Path, case_name: str):
    zonal_df = get_zonal_qois(idf, sql, case_name)
    surface_df = get_zonal_qois(idf, sql, case_name)
    return StandardData(zonal_df, surface_df)
