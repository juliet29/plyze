from loguru import logger
import xarray as xr

from plyze.utils import XArrayNames


def inflow(node_1_2_flow: list[xr.DataArray]) -> xr.DataArray:
    # TODO: need to unify this and the outflow function... its basically just a summing function.. only difference is the name of the imput...
    # logger.debug(node_1_2_flow)
    res = sum(node_1_2_flow)
    # logger.debug(res)
    assert isinstance(res, xr.DataArray)
    return res


def outflow(node_2_1_flow: list[xr.DataArray]) -> xr.DataArray:
    res = sum(node_2_1_flow)
    assert isinstance(res, xr.DataArray)
    return res


def zone_dimless_flow(
    wind_speed: xr.DataArray, zone_sum_flow: xr.DataArray, surface_areas: list[float]
):
    sum_areas = sum(surface_areas)
    return zone_sum_flow / (sum_areas * wind_speed)


def zone_dimless_temp(t_out: xr.DataArray, zone_t: xr.DataArray):
    return zone_t / t_out


def plan_flow_loss(inflow: xr.DataArray, outflow: xr.DataArray):
    return inflow - outflow


def plan_max_pressure_diff(pressure_data_for_external_nodes: list[xr.DataArray]):
    # TODO: check that they have the same timing..and dont have spaces.. if so, drop them.., should also ideally have names?
    logger.debug(pressure_data_for_external_nodes)
    for ix, da in enumerate(pressure_data_for_external_nodes):
        da.name = ix
        da.drop_vars(XArrayNames.SPACE)

    ds = xr.merge(pressure_data_for_external_nodes, combine_attrs="drop_conflicts")
    logger.debug(ds)
    return ds.max() - ds.min()
