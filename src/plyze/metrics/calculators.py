from dataclasses import dataclass
import networkx as nx

from plyze.flow_graph.interfaces import FlowGraph
from plyze.metrics.dominant_external_node import separate_dominant_nodes
from plyze.metrics.flow_paths import create_flow_paths
import statistics
from plyze.metrics.interfaces import BaseCalculator, MetricHolder
from plyze.metrics.qoi_calculator import SpaceTimeQOICalculator
from plyze.metrics.registries import MetricRegistry
from plyze.qoi_flow_graph.dim_zone_data import EnvironmentalComparisons


FMR = MetricRegistry.flow
PMR = MetricRegistry.plan


@dataclass
class PlanMetricsCalculator(BaseCalculator):
    def calc_length_metrics(self):
        self.register(PMR.area, sum([i.data.area for i in self.G.zone_nodes]))
        self.register(PMR.num_rooms, len(self.G.zone_names))

    def run(self):
        self.calculate([self.calc_length_metrics])


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


def make_metrics(G: FlowGraph, enviro: EnvironmentalComparisons):
    holder = MetricHolder()
    PlanMetricsCalculator(G, holder)()
    FlowMetricsCalculator(G, holder)()
    SpaceTimeQOICalculator(G, holder, enviro)()
    return holder
