import altair as alt
from plyze.flow_graph.io import FlowGraphModel
from rich.pretty import pretty_repr
from plyze.flow_graph.create.main import (
    make_ambient_data,
    make_flow_graph,
)

import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plyze.examples.casedata import example_casedata, example_times
from plyze.paths import ProjectPaths
from plyze.plots.altair_helpers import AltairRenderers
from plyze.plots.theme import default_theme
from plyze.qoi_flow_graph.zone_data import collate_zone_data_to_df

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
def ad():
    return make_ambient_data(example_casedata.sql)


@app.command
def fg():
    G = FlowGraphModel.read(path=ProjectPaths.sample_flow_graph_json)
    # zone = G.zone_nodes[-1]

    # return zone

    res = collate_zone_data_to_df(G)
    return res
    # ambient_data = make_ambient_data(example_casedata.sql, example_times)
    # res = update_zone_qois(G, ambient_data)
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
