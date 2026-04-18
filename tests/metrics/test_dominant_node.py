from plyze.flow_graph.create.main import make_flow_graph
from plyze.examples.casedata import example_casedata, example_times
from plyze.metrics.dominant_external_node import (
    calc_dominant_node,
    get_max_wind_pressure_at_time,
)


class TestDominantNode:

    G = make_flow_graph(example_casedata, 1.1, example_times)
    df_max = get_max_wind_pressure_at_time(G.external_nodes)

    def test_df_max(self):
        assert self.df_max.height >= len(example_times)

    def test_calc_dominant_node(self):
        dom_node = calc_dominant_node(self.df_max)
        assert type(dom_node) is str
