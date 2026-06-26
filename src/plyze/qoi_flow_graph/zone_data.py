from pathlib import Path
from typing import Callable, TypeVar, get_args

import polars as pl
import polars.selectors as cs
import xarray as xr
from loguru import logger

from plyze.flow_graph.interfaces import (
    AmbientData,
    Edge,
    ExternalNode,
    FlowGraph,
    ZoneNode,
    ZoneNodeQOINames,
)
from plyze.utils import XArrayNames

GraphVal = TypeVar("GraphVal", ZoneNode, ExternalNode, Edge)


def create_flow_graph_xarray(
    fx: Callable[[GraphVal], xr.DataArray], graph_vals: list[GraphVal]
):
    plan_data = xr.concat(
        [fx(i) for i in graph_vals],
        dim=XArrayNames.SPACE,
    )

    return plan_data


def collate_zone_data(G: FlowGraph, afn_nodes_only: bool = True) -> xr.Dataset:
    def make_df(qoi: ZoneNodeQOINames):
        if afn_nodes_only:
            nodes = [i for i in G.zone_nodes if i.data.is_in_afn]
        else:
            nodes = G.zone_nodes

        plan_array = create_flow_graph_xarray(
            lambda x: x.data.get_qoi_array(qoi), nodes
        )
        plan_array.name = qoi
        return plan_array

    # basically concat and turn into dataframe..

    das = [make_df(i) for i in get_args(ZoneNodeQOINames)]
    ds = xr.merge(das)
    # ds = xr.Dataset(das)

    return ds


# TODO: this may need a different location for the AmbientData..
def collate_ambient_data(data: AmbientData):
    lst = []
    for k, v in data._asdict().items():
        v.name = k
        v1 = v.drop_vars(
            XArrayNames.SPACE
        )  # TODO: drop_vars at the original creation site
        lst.append(v1)

    return xr.merge(lst)

    # dfs = [convert_xarray_to_polars(v, name=k) for k, v in dict_.items()]
    # return pl.concat(dfs, how="align")


def read_ambient_data(ambient_path: Path):
    # TODO: this is duplicated in nvflow and that should be avoided.. (logic for overriding times..)
    df = (
        pl.read_csv(
            ambient_path, schema_overrides={XArrayNames.DATETIME: pl.Datetime("us")}
        )
        .sort(XArrayNames.DATETIME)
        .unique(XArrayNames.DATETIME)
    )
    logger.debug(df.shape)
    datetimes = df.get_column(XArrayNames.DATETIME).to_numpy()
    data = df.select(cs.float()).to_dict()
    da = {
        k: xr.DataArray(data=v, coords={XArrayNames.DATETIME: datetimes})
        for k, v in data.items()
    }

    return AmbientData(**da)


# More QOIS -> not stored on the nodes # TODO: add to QOI registry?
#
