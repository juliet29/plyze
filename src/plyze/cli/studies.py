import altair as alt
from plyze.flow_graph.create.main import make_flow_graph

import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plyze.examples.casedata import example_casedata, example_times
from plyze.plots.altair_helpers import AltairRenderers
from plyze.plots.theme import default_theme

app = App()


def keep():
    _ = example_casedata
    default_theme()
    logger.debug("")
    plt.plot()
    example_casedata.sql


### ------- START COMMANDS ---------


@app.command
def fg():
    G = make_flow_graph(example_casedata, 1.1, dt=example_times)
    extn = G.external_nodes[0]
    print(extn.data.external_wind_pressure.datetimes)
    # e1 = G.edges_with_data[0]
    # print(e1)


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
