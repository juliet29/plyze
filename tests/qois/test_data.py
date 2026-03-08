import polars as pl
from plys.paths import ProjectPaths
from plys.qoi.data.data import to_dataframe_with_spaces, to_multi_data
from plys.qoi.data.interfaces import QOIandData
from plys.qoi.data.spaces import create_space_df
from plys.qoi.registries.main import QOIRegistry


def test_create_space_df():
    res = create_space_df(ProjectPaths.sample_idf)
    assert isinstance(res, pl.DataFrame)
    assert res["space_names"].len() > 1


def test_qoi_data_creation():
    res = to_dataframe_with_spaces(
        QOIRegistry.flow_12, ProjectPaths.sample_idf, ProjectPaths.sample_sql
    )
    assert isinstance(res.dataframe, pl.DataFrame)
    assert res.dataframe["space_names"].len() > 1


def test_qoi_data_creation_with_custom_qoi():
    res = to_dataframe_with_spaces(
        QOIRegistry.custom.net_flow, ProjectPaths.sample_idf, ProjectPaths.sample_sql
    )
    assert isinstance(res.dataframe, pl.DataFrame)


def test_multidata():
    single_data = to_dataframe_with_spaces(
        QOIRegistry.custom.net_vent_heat_gain,
        ProjectPaths.sample_idf,
        ProjectPaths.sample_sql,
    )
    df = to_multi_data(
        [
            QOIRegistry.custom.net_vent_heat_gain,
            QOIRegistry.vent_vol,
            QOIRegistry.mix_vol,
        ],
        ProjectPaths.sample_idf,
        ProjectPaths.sample_sql,
    )
    assert isinstance(single_data.dataframe, pl.DataFrame)
    assert single_data.dataframe.height == df.height
    assert single_data.dataframe.width + 2 == df.width
    assert QOIRegistry.vent_vol.nickname in df.columns
    assert QOIRegistry.mix_vol.nickname in df.columns


def test_custom_qoi_with_non_basic_fx():

    res = QOIandData(
        QOIRegistry.custom.unique_wind_pressure, ProjectPaths.sample_sql
    ).original_arr
    spaces = res.space_names.to_series().to_list()
    assert len(spaces) == len(set(spaces))
