from dataclasses import dataclass
from pathlib import Path
from typing import Callable, NamedTuple

from pydantic import BaseModel
from utils4plans.io import read_json, write_json
from plyze.flow_graph.interfaces import FlowGraph


class Metric(NamedTuple):
    name: str
    proper_name: str


class MetricAndData(NamedTuple):
    metric: Metric
    value: float


class MetricHolder(BaseModel):
    holder_dict: dict[str, float] = {}

    def update(self, metric: Metric, value: float):
        # TODO: raise warning on overwrite?
        self.holder_dict[metric.name] = value

    def write(self, path: Path):
        write_json(self.model_dump(), path, OVERWRITE=True)

    @classmethod
    def read(cls, path: Path):
        data = read_json(path)
        model = cls.model_validate(data)
        return model


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
