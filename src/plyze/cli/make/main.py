from utils4plans.logconfig import logset
import altair as alt

from cyclopts import App

from plyze.fpviz.main import plan_plot
from plyze.paths import ProjectPaths
from plyze.plots.altair_helpers import AltairRenderers
from plyze.plots.theme import default_theme
from loguru import logger
from plyze.cli.make.jpg import jpg
from plyze.cli.make.qoi import qoi

app = App()
app.command(jpg)
app.command(qoi)


def keep():
    default_theme()
    logger.debug("")


### ------- BEGIN COMMANDS ----------

### ------ SHOW FLOOR PLAN


@app.command()
def show_plan():
    plan_plot(ProjectPaths.sample_idf)


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
