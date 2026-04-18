import altair as alt
from plyze.flow_graph.create.main import make_flow_graph

import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plyze.examples.casedata import example_casedata, example_times
from plyze.metrics.dominant_external_node import (
    calc_dominant_node,
    calc_value_counts,
    get_max_wind_pressure_at_time,
)
from plyze.plots.altair_helpers import AltairRenderers
from plyze.plots.theme import default_theme

app = App()


def keep():
    default_theme()
    logger.debug("")
    plt.plot()

    _ = example_casedata
    _ = example_times

    _ = make_flow_graph


### ------- START COMMANDS ---------


@app.command
def fg():
    G = make_flow_graph(example_casedata, 1.1, example_times)
    df_max = get_max_wind_pressure_at_time(G.external_nodes)
    print(calc_value_counts(df_max))
    print(calc_dominant_node(df_max))


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
