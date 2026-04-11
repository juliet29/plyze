# each node knows its level
# metrics taken from Ostwald 2011

from loguru import logger
from plyze.jpg.interfaces import JPGraph
from utils4plans.lists import sort_and_group_objects_dict
from plyze.jpg.interfaces import JPGMetrics
from plyze.jpg.scalable_graphs import make_diamond_graph


def calculate_total_depth(G: JPGraph):
    # sort and group ndoes based on level
    nodes = G.jpnodes
    levels = sort_and_group_objects_dict(nodes, lambda x: x.data.level)

    total_depth = 0
    for level, nodes in levels.items():
        val = level * len(nodes)
        # logger.debug(f"level: {level}, n_nodes: {len(nodes)}")
        total_depth += val

    return total_depth


def calculate_mean_depth(
    G: JPGraph, total_depth: float, carrier_node_present: bool = True
):
    if carrier_node_present:
        return total_depth / (
            G.num_nodes - 1
        )  # TODO: this should be -1 if the carrier is included as one of the nodes
    return total_depth / G.num_nodes


def calculate_relative_asymmetry(G: JPGraph, mean_depth: float):
    return 2 * (mean_depth - 1) / (G.num_nodes - 2)


def calculate_relative_asymmetry_full(G: JPGraph, carrier_node_present: bool):
    total_depth = calculate_total_depth(G)
    mean_depth = calculate_mean_depth(G, total_depth, carrier_node_present)
    relative_asymmetry = calculate_relative_asymmetry(G, mean_depth)
    return relative_asymmetry


def calculate_diamond_relative_asymmetry(k: int):
    G = make_diamond_graph(k, True)
    ra = calculate_relative_asymmetry_full(G, carrier_node_present=False)
    logger.debug(ra)


def calculate_jpg_metrics(G: JPGraph):
    total_depth = calculate_total_depth(G)
    mean_depth = calculate_mean_depth(G, total_depth)
    relative_asymmetry = calculate_relative_asymmetry(G, mean_depth)
    # control_value = calculate_control_value(G)
    # TODO: the control value will be the max control value or a list.. / some special way of going into the dataframe if want all ..

    return JPGMetrics(
        graph_name=G.graph_name,
        total_depth=total_depth,
        mean_depth=mean_depth,
        relative_asymmetry=relative_asymmetry,
    )
