from dataclasses import dataclass
from typing import get_args
import networkx as nx
from plan2eplus.geometry.contact_points import CardinalEntries
from utils4plans.lists import chain_flatten

from plyze.flow_graph.interfaces import FlowGraph
from plyze.metrics.helpers.dominant_external_node import separate_dominant_nodes
from plyze.metrics.helpers.flow_paths import create_flow_paths
import statistics
from plyze.metrics.helpers.facade_groups import FACADE_GROUPS
from plyze.metrics.interfaces import BaseCalculator, MetricHolder
from plyze.metrics.registries import MetricRegistry


FMR = MetricRegistry.flow
PMR = MetricRegistry.plan


@dataclass
class PlanMetricsCalculator(BaseCalculator):
    def calc_length_metrics(self):
        self.register(PMR.area, sum([i.data.area for i in self.G.zone_nodes]))
        self.register(PMR.num_rooms, len(self.G.zone_names))

    def calculate_facades(self):
        window_edges = [
            i for i in self.G.edges_with_data if i.data.surface_type == "Window"
        ]
        edge_values = chain_flatten([[i.u, i.v] for i in window_edges])
        cardinal_values = set(
            [i for i in edge_values if i in get_args(CardinalEntries)]
        )
        cardinal_intials = frozenset([i[0].upper() for i in cardinal_values])
        facade_group = FACADE_GROUPS[cardinal_intials]
        self.register(PMR.facades_window_group, facade_group)

    def run(self):
        self.calculate([self.calc_length_metrics, self.calculate_facades])


@dataclass
class FlowMetricsCalculator(BaseCalculator):
    @property
    def dominant_node(self):
        nodes = separate_dominant_nodes(self.G.external_nodes)
        return nodes.main

    @property
    def paths(self):
        return create_flow_paths(
            self.G
        )  # TODO: wonder if this should depend on the dominant node explicity, so don't calculate twice?

    def calc_num_paths(self):
        self.register(FMR.num_paths, len(self.paths))

    def calc_length_metrics(self):
        lengths = [len(i) for i in self.paths]
        # NOTE: this is a tempoerary fix, if there are no paths, then something is wrong with the graph..
        if not lengths:
            lengths = [0]

        self.register(FMR.avg_path_length, statistics.mean(lengths))

        self.register(FMR.mode_path_length, statistics.mode(lengths))

        self.register(FMR.len_shortest_path, min(lengths))

    def calc_dominant_node_metrics(self):
        deg = nx.degree(self.G, self.dominant_node.name)
        assert isinstance(deg, int)
        self.register(FMR.degree_dom_node, deg)

    def run(self):
        self.calculate(
            [
                self.calc_num_paths,
                self.calc_length_metrics,
                self.calc_dominant_node_metrics,
            ]
        )


def make_metrics(G: FlowGraph):
    holder = MetricHolder()
    PlanMetricsCalculator(G, holder)()
    FlowMetricsCalculator(G, holder)()
    return holder
