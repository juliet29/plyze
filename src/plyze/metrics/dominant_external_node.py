from typing import NamedTuple
import polars as pl

from plyze.flow_graph.interfaces import ExternalNode
from plyze.qoi.xarray_helpers import convert_xarray_to_polars
from plyze.qoi.registries.main import QOIRegistry
from utils4plans.lists import get_unique_one

wp = QOIRegistry.wind_pressure.nickname
drn = "direction"
drn_max = f"direction of max {wp}"


def get_max_wind_pressure_at_time(nodes: list[ExternalNode]):

    def prep_df(node: ExternalNode):
        df = convert_xarray_to_polars(node.data.external_wind_pressure, name=node.name)
        df2 = df.unpivot(
            index="datetimes",
            on=node.name,
            variable_name=drn,
            value_name=wp,
        )

        return df2

    dfs = [prep_df(i) for i in nodes]
    df = pl.concat(dfs, how="vertical")
    df_max = df.group_by("datetimes").agg(
        pl.col(wp).max().alias(f"max {wp}"),
        pl.col(drn).max_by(wp).alias(drn_max),
    )
    return df_max


def calc_value_counts(df: pl.DataFrame):
    # NOTE: not using yet, but may be valueable if want to ask questions about HOW dominant a node is..
    return df.select(pl.col(drn_max).value_counts(normalize=True, sort=True)).unnest(
        drn_max
    )


def calc_dominant_node(df: pl.DataFrame):
    return df.select(pl.col(drn_max).mode().first()).to_series().to_list()[0]


class DistinguishedExternalNodes(NamedTuple):
    main: ExternalNode
    other: list[ExternalNode]


def separate_dominant_nodes(nodes: list[ExternalNode]):
    df_max = get_max_wind_pressure_at_time(nodes)
    dominant_node_name = calc_dominant_node(df_max)
    dom_node = get_unique_one(nodes, lambda x: x.name == dominant_node_name)

    other_nodes = [i for i in nodes if not i.name == dominant_node_name]

    return DistinguishedExternalNodes(dom_node, other_nodes)
