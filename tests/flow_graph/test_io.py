from pathlib import Path
from plyze.flow_graph.create.main import make_flow_graph


from plyze.examples.casedata import example_casedata, example_times
from plyze.flow_graph.io import FlowGraphModel
import tempfile


class TestFlowGraphIO:

    G = make_flow_graph(example_casedata, 1.1, example_times)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td)
        json_path = path / "out.json"
        data_folder = "data"

        data_path = json_path.parent / data_folder
    FlowGraphModel.write(G, json_path, data_folder)

    def test_write(self):
        assert len(list(self.data_path.iterdir())) > 2

    def test_read(self):
        print(list(self.data_path.iterdir()))
        print(list((self.data_path / "bathroom_5").iterdir()))
        graph = FlowGraphModel.read(self.json_path)
        assert len(graph) > 2
        assert len(graph.zone_nodes) > 2
