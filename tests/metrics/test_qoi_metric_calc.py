from plyze.flow_graph.create.main import make_flow_graph
from plyze.examples.casedata import example_casedata, example_times
from plyze.metrics.interfaces import MetricHolder
from plyze.metrics.qoi_calculator import SpaceTimeQOICalculator
from plyze.paths import ProjectPaths
from plyze.qoi_flow_graph.zone_data import make_enviro


class TestSpaceTimeCalculator:

    G = make_flow_graph(example_casedata, 1.1, example_times)

    def test_median_calc(self):
        holder = MetricHolder()
        enviro = make_enviro(ProjectPaths.sample_sql)
        SpaceTimeQOICalculator(self.G, holder, enviro)()
        assert "median_vent_vol" in holder.holder_dict.keys()
