import altair as alt
import matplotlib.pyplot as plt
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset

from plys.examples.casedata import ex
from plys.qoi.data.interfaces import CaseQOIandData
from plys.qoi.data.outputs import consolidate_data, get_surface_qois
from plys.qoi.plots.altair_helpers import AltairRenderers
from plys.qoi.plots.theme import default_theme

app = App()


def keep():
    default_theme()
    logger.debug("")
    plt.plot()


### ----- DATA --------
@app.command()
def get():
    res = get_surface_qois(*ex)
    logger.debug(res)
    logger.debug(res.columns)


@app.command()
def cons():
    df1 = get_surface_qois(*ex)
    df2 = get_surface_qois(*ex)
    case_names = ["c1", "c2"]
    case_datas = [CaseQOIandData(case, df) for case, df in zip(case_names, [df1, df2])]
    df = consolidate_data(case_datas)
    logger.debug(df)


### ------- SINGLE PLOTS


# def plot_vol():
#     qoid = data_create()
#     logger.debug(qoid.dataframe)
#     chart = corr_plot(qoid)
#     chart.show()
#
#
# @app.command()
# def plot_surfs():
#     qoid = custom_qoi()  # data_create()
#     logger.debug(qoid.dataframe)
#
#     chart = surface_corr_plot(qoid)
#     chart.show()


### ------- MULTI PLOTS
# @app.command()
# def plot_vol_many():
#     c = zone_qois(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
#     c.show()
#
#
# @app.command()
# def plot_surfs_many():
#     c = surface_qois(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
#     c.show()


### ------- BIVAR PLORS

### ---- JPG ----


### --- CLUSTERING ----
# @app.command()
# def kn():
#     iris = load_iris(as_frame=True)
#     X = iris.data[["sepal length (cm)"]].to_numpy()
#     model, labels = fit_samples(X, 3)
#     logger.debug(model)
#     logger.debug(labels)
#     df = prep_cluster_df(X, labels, ["sepal len"])
#     logger.debug(df)
#     chart = show_clusters(df, "sepal len")
#     chart.show()

# model = fit_neighbors(X, 3)
# return model.predict()
# return show_neighbors_one(model, [[1]])


### ------- END COMMANDS ---------


def main():
    AltairRenderers.set_renderer()
    alt.theme.enable("default_theme")
    logset(to_stderr=True)
    app()


if __name__ == "__main__":
    main()
