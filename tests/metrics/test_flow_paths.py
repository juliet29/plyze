from plyze.flow_graph.create.main import make_flow_graph
from plyze.metrics.flow_paths import create_flow_paths, create_st_graph


from plyze.examples.casedata import example_casedata, example_times


class TestFlowPaths:
    G = make_flow_graph(example_casedata, 1.1, example_times)

    def test_create_st_graph(self):
        gst = create_st_graph(self.G, "NORTH", "WEST")
        assert "SOUTH" not in gst.nodes
        assert "EAST" not in gst.nodes

    def test_create_flow_graph(self):
        paths = create_flow_paths(self.G)
        assert len(paths) > 2
