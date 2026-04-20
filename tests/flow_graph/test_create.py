from plyze.flow_graph.create.main import make_flow_graph
from plyze.examples.casedata import example_casedata, example_times


class TestFlowGraph:

    G = make_flow_graph(example_casedata, 1.1)

    def test_valid_edges(self):
        # each node has at least one edge (may not be true for all graphs, but then something is wrong.. )
        assert len(list(self.G.edges)) >= len(self.G.all_names)

    def test_more_external_nodes(self):
        assert len(self.G.all_names) > len(self.G.zone_names)

    def test_valid_edge_data(self):
        extn = self.G.external_nodes[0]
        assert extn.data.external_wind_pressure.data.any()
        # TODO: later -> check that it is in a desirable format
        # assert extn.name == extn.data.external_wind_pressure.name
        #
        #

    def test_datetimes(self):
        G = make_flow_graph(example_casedata, 1.1, example_times)
        extn = G.external_nodes[0]
        assert len(extn.data.external_wind_pressure.datetimes) == len(example_times)

    def test_datetimes_zones(self):
        G = make_flow_graph(example_casedata, 1.1, example_times)
        zone = G.zone_nodes[0]
        assert len(zone.data.ventilation_volume.datetimes) == len(example_times)
