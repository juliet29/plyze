import statistics
from dataclasses import dataclass

import networkx as nx

from plyze.flow_graph.interfaces import FlowGraph
from plyze.metrics.helpers.flow_paths import create_flow_paths, organize_external_nodes
from plyze.metrics.interfaces import BaseCalculator, MetricHolder
from plyze.metrics.registries import MetricRegistry
from plyze.qoi.xarray_helpers import CardinalNameLiteral

FMR = MetricRegistry.flow
PMR = MetricRegistry.plan


@dataclass
class PlanMetricsCalculator(BaseCalculator):
    def calc_length_metrics(self):
        # defaults to using all the rooms in the plan, not just those in the AFN
        self.register(PMR.area, sum([i.data.area for i in self.G.zone_nodes]))
        self.register(PMR.num_rooms, len(self.G.zone_names))

    # def calculate_facades(self):
    #     window_edges = [
    #         i for i in self.G.edges_with_data if i.data.surface_type == "Window"
    #     ]
    #     edge_values = chain_flatten([[i.u, i.v] for i in window_edges])
    #     cardinal_values = set(
    #         [i for i in edge_values if i in get_args(CardinalEntries)]
    #     )
    #     cardinal_intials = frozenset([i[0].upper() for i in cardinal_values])
    #     facade_group = FACADE_GROUPS[cardinal_intials]
    #     self.register(PMR.facades_window_group, facade_group)
    #
    def run(self):
        self.calculate([self.calc_length_metrics])


@dataclass
class FlowMetricsCalculator(BaseCalculator):
    dominant_node_drn: CardinalNameLiteral | None

    @property
    def distinguished_external_nodes(self):
        try:
            nodes = organize_external_nodes(
                self.G.external_nodes, self.dominant_node_drn
            )
        except ValueError:
            return None
        return nodes

    @property
    def paths(self):
        if not self.distinguished_external_nodes:
            return []

        return create_flow_paths(self.G, self.distinguished_external_nodes)

    def calc_num_paths(self):
        self.register(FMR.num_paths, len(self.paths))

    def calc_length_metrics(self):
        lengths = [len(i) for i in self.paths]

        if not lengths:
            lengths = [0]

        self.register(FMR.avg_path_length, statistics.mean(lengths))

        self.register(FMR.mode_path_length, statistics.mode(lengths))

        self.register(FMR.len_shortest_path, min(lengths))

        self.register(FMR.len_longest_path, max(lengths))

    def calc_dominant_node_metrics(self):
        if not self.distinguished_external_nodes:
            deg = 0
        else:
            deg = nx.degree(self.G, self.distinguished_external_nodes.main.name)
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
    FlowMetricsCalculator(G, holder, None)()
    return holder
