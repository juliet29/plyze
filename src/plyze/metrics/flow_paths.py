from plyze.flow_graph.interfaces import ExternalNode, FlowGraph
from loguru import logger
from rich.pretty import pretty_repr
from plyze.metrics.dominant_external_node import separate_dominant_nodes
import networkx as nx


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


def create_flow_paths(G: FlowGraph):
    ext_nodes = separate_dominant_nodes(G.external_nodes)
    dom_node = ext_nodes.main

    # for now, don't distinguish the end points, just collect all the paths
    all_paths = []

    for node in ext_nodes.other:
        gst = create_st_graph(G, dom_node.name, node.name)
        paths = nx.all_simple_paths(gst, source=dom_node.name, target=node.name)
        all_paths.extend(list(paths))

    return all_paths
