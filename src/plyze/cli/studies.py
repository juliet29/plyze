from pathlib import Path
import altair as alt
from rich.pretty import pretty_repr
from plyze.flow_graph.create.main import make_flow_graph

import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plyze.examples.casedata import example_casedata, example_times
from plyze.flow_graph.io import FlowGraphModel
from plyze.paths import ProjectPaths
from plyze.plots.altair_helpers import AltairRenderers
from plyze.plots.theme import default_theme
import tempfile

app = App()


def keep():
    default_theme()
    logger.debug("")
    plt.plot()

    pretty_repr("")

    _ = tempfile

    _ = example_casedata
    _ = example_times

    _ = make_flow_graph


### ------- START COMMANDS ---------


def test_flow_graph_io():
    G = make_flow_graph(example_casedata, 1.1, example_times)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td)
        json_path = path / "out.json"
        FlowGraphModel.write(
            G,
            json_path,
            path,
            # ProjectPaths.test_write_flow_graph,
        )
        print((path.iterdir()))


@app.command
def fg():
    G = make_flow_graph(example_casedata, 1.1, example_times)

    path = ProjectPaths.test_write_flow_graph
    json_path = path / "out.json"
    FlowGraphModel.write(
        G,
        json_path,
        path,
    )
    graph = FlowGraphModel.read(json_path)
    print((graph))

    # gst = create_st_graphvwG, "NORTH", "WEST"v  # TODO: test!
    # print(pretty_repr(list(gst.edges)))
    # return make_metrics(G)


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
