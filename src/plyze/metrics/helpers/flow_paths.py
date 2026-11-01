import networkx as nx
from loguru import logger
from rich.pretty import pretty_repr

from plyze.flow_graph.interfaces import ExternalNode, FlowGraph
from plyze.metrics.helpers.dominant_external_node import (
    DistinguishedExternalNodes,
    separate_dominant_nodes_based_on_wind_pressure,
    separate_dominant_nodes_given,
)
from plyze.qoi.xarray_helpers import CardinalNameLiteral


def create_st_graph(flow_graph: FlowGraph, source: str, target: str):
    G = nx.Graph()
    # G.add_node(source)
    # G.add_node(target)
    G.add_nodes_from(flow_graph.zone_names + [source, target])

    filtered_edges = [
        i for i in flow_graph.edges if i[0] in G.nodes and i[1] in G.nodes
    ]

    G.add_edges_from(filtered_edges)

    return G


def show_paths(node: ExternalNode, paths: list):
    logger.debug(pretty_repr({"nb": node.name, "paths": list(paths)}))


def organize_external_nodes(
    nodes: list[ExternalNode], dominant_node_name: CardinalNameLiteral | None = None
):
    if dominant_node_name:
        ext_nodes = separate_dominant_nodes_given(nodes, dominant_node_name)
    else:
        ext_nodes = separate_dominant_nodes_based_on_wind_pressure(nodes)
    return ext_nodes


def create_flow_paths(
    G: FlowGraph, distingished_external_nodes: DistinguishedExternalNodes
):
    dom_node = distingished_external_nodes.main

    all_paths = []

    for node in distingished_external_nodes.other:
        gst = create_st_graph(G, dom_node.name, node.name)
        paths = nx.all_simple_paths(gst, source=dom_node.name, target=node.name)
        all_paths.extend(list(paths))

    return all_paths
