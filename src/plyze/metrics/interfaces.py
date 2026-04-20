from dataclasses import dataclass
from pathlib import Path
import networkx as nx
from typing import Callable, NamedTuple

from pydantic import BaseModel
from utils4plans.io import read_json, write_json
from plyze.flow_graph.interfaces import FlowGraph
from plyze.metrics.dominant_external_node import separate_dominant_nodes
from plyze.metrics.flow_paths import create_flow_paths
import statistics


class Metric(NamedTuple):
    name: str
    proper_name: str


class MetricAndData(NamedTuple):
    metric: Metric
    value: float


class PlanMetricRegistry:
    area = Metric("area", "Area [m2]")
    num_rooms = Metric("num_rooms", "Number of Rooms")


class FlowMetricRegistry:
    num_paths = Metric("num_paths", "Number of Paths")
    avg_path_length = Metric("avg_path_length", "Average Length of Paths")
    mode_path_length = Metric("mode_path_length", "Most Frequent Length of Paths")
    len_shortest_path = Metric("len_shortest_path", "Length of Shortest Path")
    degree_dom_node = Metric("degree_dom_node", "Degree of Dominant Node")

    dominant_node_direction = Metric(
        "dominant_node_direction", "Direction of Dominant Node"
    )
    mean_depth_dom_node = Metric("mean_depth_dom_node", "Mean Depth of Dominant Node")


class MetricRegistry:
    flow = FlowMetricRegistry
    plan = PlanMetricRegistry


class MetricHolder(BaseModel):
    holder_dict: dict[str, float] = {}

    def update(self, metric: Metric, value: float):
        # TODO: raise warning on overwrite?
        self.holder_dict[metric.name] = value

    def write(self, path: Path):
        write_json(self.model_dump(), path, OVERWRITE=True)
        # df = pl.DataFrame(self.holder_dict)
        # df.write_csv(path)

    @classmethod
    def read(cls, path: Path):
        data = read_json(path)
        model = cls.model_validate(data)
        return model


# TODO: put in own place..
FMR = MetricRegistry.flow
PMR = MetricRegistry.plan


@dataclass
class BaseCalculator:
    G: FlowGraph
    holder: MetricHolder

    def register(self, metric: Metric, value: float):
        self.holder.update(metric, value)

    def calculate(self, functions: list[Callable]):
        for f in functions:
            f()

    def run(self) -> None: ...

    def __call__(self):
        self.run()


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


def make_metrics(G: FlowGraph):
    holder = MetricHolder()
    PlanMetricsCalculator(G, holder)()
    FlowMetricsCalculator(G, holder)()
    return holder
