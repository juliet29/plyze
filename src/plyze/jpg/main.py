from pathlib import Path
from utils4plans.lists import get_unique_one
from datetime import datetime

from plan2eplus.ezcase.ez import EZ
from plan2eplus.ops.afn.ezobject import Airboundary
from plan2eplus.ops.subsurfaces.ezobject import Subsurface
from plan2eplus.ops.zones.ezobject import Zone
from plyze.jpg.interfaces import JPGraph, JPNode, JPNodeData
import networkx as nx
from utils4plans.sets import set_difference

# from plyze.qoi.custom_qois import find_drn
# from plyze.qoi.registry import QOIRegistry, QOIandData, select_time

# from plyze.qoi.registries.custom import find_drn_in_name

from plyze.qoi.xarray_helpers import find_drn_in_name, select_time
from plyze.qoi.registries.main import QOIRegistry
from plyze.qoi.data.interfaces import QOIandData


def set_levels(G: JPGraph):
    def update_level(node_name: str, level: int):
        node = G.get_jpnode_by_name(node_name)
        # NOTE: this is not very functional, should create a new data ..
        node.data.level = level
        G.update_jpnode(node.name, node.data)

    # assert carrier node has been set
    carrier_node = get_unique_one(G.jpnodes, lambda x: x.data.is_carrier)
    # set level of carrier node
    # update_level(carrier_node, 0)

    # set others based on distance from carrier..
    other_nodes = set_difference(G.nodes, [carrier_node.name])
    for node in other_nodes:
        try:
            distance = nx.shortest_path_length(G, source=carrier_node.name, target=node)
            # logger.debug(f"{carrier_node.name}, {node}, {distance}")
            update_level(node, int(distance))
        except nx.NetworkXNoPath:
            # TODO: the reason the metrics is failing is because maybe including invalid nodes in the count... maybe need a filtering function that takes only positive levels
            # NOTE: the node is disconnected, assign is a negative value for now, potentially delete later..
            update_level(node, -1)

    return G


def idf_to_jpgraph(
    graph_name: str, idf_path: Path, sql_path: Path, datetime_: datetime
):
    case = EZ(idf_path)

    def make_jpnode_from_zone(zone: Zone):
        return JPNode(name=zone.room_name, data=JPNodeData())

    def make_edge_from_surface(
        afn_surface: Subsurface | Airboundary, carrier_node_name: str
    ):
        node_names = [i.room_name for i in case.objects.zones] + [carrier_node_name]
        e = afn_surface.edge
        if e.space_a in node_names and e.space_b in node_names:
            return (e.space_a, e.space_b)

    def make_carrier_jpnode():
        # TODO: this should be pretty flexible, may want to make the carrier node be based on some other factor..
        wind_pressure_data = QOIandData(
            QOIRegistry.custom.unique_wind_pressure, sql_path
        ).original_arr
        max_node_at_time = (
            select_time(wind_pressure_data, datetime_).idxmax().to_dict()["data"]
        )
        max_node_as_drn = find_drn_in_name(max_node_at_time)
        return JPNode(name=max_node_as_drn, data=JPNodeData(is_carrier=True, level=0))

    carrier_node = make_carrier_jpnode()

    jpnodes = [make_jpnode_from_zone(i) for i in case.objects.zones] + [carrier_node]
    edges = [
        make_edge_from_surface(i, carrier_node.name)
        for i in case.objects.subsurfaces + case.objects.airboundaries
    ]
    filtered_edges = [i for i in edges if i]

    G = JPGraph.create(graph_name, jpnodes, filtered_edges)

    leveled_graph = set_levels(G)

    return leveled_graph
