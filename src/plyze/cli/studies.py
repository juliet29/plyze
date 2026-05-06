import altair as alt
from plyze.flow_graph.io import FlowGraphModel
from rich.pretty import pretty_repr
from plyze.flow_graph.create.main import make_flow_graph

import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plyze.examples.casedata import example_casedata, example_times
from plyze.paths import ProjectPaths
from plyze.plots.altair_helpers import AltairRenderers
from plyze.plots.theme import default_theme

app = App()


def keep():
    default_theme()
    logger.debug("")
    plt.plot()

    pretty_repr("")

    _ = example_casedata
    _ = example_times

    _ = make_flow_graph


### ------- START KEEP COMMANDS ---------
@app.command
def make_flow_graph_example():
    G = make_flow_graph(example_casedata, 1.1, example_times)
    FlowGraphModel.write(G, ProjectPaths.sample_flow_graph_json, "data")


### ------- START TEMP COMMANDS ---------


@app.command
def fg():
    G = FlowGraphModel.read(
        path=ProjectPaths.sample_flow_graph_json, sql=example_casedata.sql
    )
    return G.ambient_data
    # return update_zone_qois(G)
    # zone = G.zone_nodes[-1]
    # return GraphQOICalculator(GraphQOIHolder(), G, zone).zone_edges


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
