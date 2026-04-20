from datetime import datetime
from plan2eplus.ezcase.ez import EZ
from plyze.flow_graph.create.edge import make_edges_for_graph
from plyze.flow_graph.create.external_node import make_external_nodes
from plyze.flow_graph.create.zone import make_zones_for_graph
from plyze.flow_graph.interfaces import FlowGraph
from plyze.utils import CaseData


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
