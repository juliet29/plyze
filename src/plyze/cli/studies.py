import altair as alt
from rich.pretty import pretty_repr
from plyze.flow_graph.create.main import make_flow_graph

import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plyze.examples.casedata import example_casedata, example_times
from plyze.metrics.interfaces import calc_metrics
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


### ------- START COMMANDS ---------


@app.command
def fg():
    G = make_flow_graph(example_casedata, 1.1, example_times)
    # gst = create_st_graph(G, "NORTH", "WEST")  # TODO: test!
    # print(pretty_repr(list(gst.edges)))
    return calc_metrics(G)


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
