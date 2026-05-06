from datetime import datetime
from pathlib import Path
from plan2eplus.ezcase.ez import EZ
from plyze.flow_graph.create.edge import make_edges_for_graph
from plyze.flow_graph.create.external_node import make_external_nodes
from plyze.flow_graph.create.zone import make_zones_for_graph
from plyze.flow_graph.interfaces import AmbientData, FlowGraph
from plyze.qoi.data.interfaces import QOIandData
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.xarray_helpers import select_time
from plyze.qoi_flow_graph.graph_qoi import GraphQOICalculator
from plyze.qoi_flow_graph.graph_qoi_interfaces import GraphQOIHolder
from plyze.utils import CaseData


def make_ambient_data(sql: Path, dt: list[datetime] = []):
    QRS = QOIRegistry.site
    ambient_data = AmbientData(
        *[
            QOIandData(i, sql).original_arr
            for i in [QRS.t_out, QRS.wind_speed, QRS.wind_direction]
        ]
    )
    if dt:
        ambient_data = AmbientData(*[select_time(i, dt) for i in ambient_data])
    return ambient_data


def make_flow_graph(
    case_data: CaseData, cardinal_expansion_factor: float, dt: list[datetime] = []
):
    case = EZ(case_data.idf)

    external_nodes = make_external_nodes(
        case, case_data.sql, cardinal_expansion_factor, dt
    )
    zones = make_zones_for_graph(case, case_data.sql, dt)
    edges = make_edges_for_graph(case, case_data.sql, dt)

    G = FlowGraph()
    G.add_flow_nodes(external_nodes + zones)
    G.add_flow_edges(edges)

    return G


def update_zone_qois(G: FlowGraph, ambient_data: AmbientData):
    zone = G.zone_nodes[-1]
    new_qoi_calculator = GraphQOICalculator(GraphQOIHolder(), G, zone, ambient_data)
    new_qoi_calculator.run()
    holder = new_qoi_calculator.holder.holder_dict
    return holder
