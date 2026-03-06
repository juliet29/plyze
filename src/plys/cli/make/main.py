from utils4plans.logconfig import logset
import altair as alt

from cyclopts import App

from plys.fpviz.main import plan_plot
from plys.paths import ProjectPaths
from plys.qoi.registry import AltairRenderers
from plys.qoi.theme import default_theme
from loguru import logger


app = App()


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
