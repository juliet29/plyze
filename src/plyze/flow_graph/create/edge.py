from pathlib import Path
from datetime import datetime
from plan2eplus.ezcase.ez import EZ
from plan2eplus.ezcase.objects import Subsurface
import xarray as xr
from plan2eplus.ops.afn.ezobject import Airboundary


from plyze.flow_graph.interfaces import Edge, EdgeData
from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.xarray_helpers import get_data_by_space_name, select_time


def make_edge_from_surface(
    afn_surface: Subsurface | Airboundary, flow_in: xr.DataArray, flow_out: xr.DataArray
):
    e = afn_surface.edge
    return Edge(
        e.space_a,
        e.space_b,
        # TODO: run some tests on this!
        data=EdgeData(
            flow_in=get_data_by_space_name(flow_in, afn_surface.name),
            flow_out=get_data_by_space_name(flow_out, afn_surface.name),
        ),
    )


def make_edges_for_graph(case: EZ, sql_path: Path, dt: list[datetime] = []):
    afn_surfaces = case.objects.airflow_network.afn_surfaces

    flow_in = QOIandData(QOIRegistry.flow_in, sql_path).original_arr
    flow_out = QOIandData(QOIRegistry.flow_out, sql_path).original_arr

    if dt:
        flow_in = select_time(flow_in, dt)
        flow_out = select_time(flow_out, dt)

    edges = [make_edge_from_surface(i, flow_in, flow_out) for i in afn_surfaces]
    return edges
