import altair as alt
from plan2eplus.ezcase.ez import EZ
from plyze.flow_graph.create.external_node import make_external_nodes
from plyze.flow_graph.io import FlowGraphModel
from rich.pretty import pretty_repr
from plyze.flow_graph.create.main import (
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
from plyze.qoi_flow_graph.calculators.plan import PlanQOICalculator
from plyze.qoi_flow_graph.interfaces import GraphQOIHolder

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
    case = EZ(example_casedata.idf)
    res = make_external_nodes(
        case, example_casedata.sql, cardinal_expansion_factor=1.1, dt=example_times
    )
    return


@app.command
def fg():
    G = FlowGraphModel.read(path=ProjectPaths.sample_flow_graph_json)
    holder = GraphQOIHolder()
    pq = PlanQOICalculator(holder, "", G)
    pq.run()

    # TODO: think if the name is needed for the calculator alwayss...

    return pq.holder.holder_dict


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
