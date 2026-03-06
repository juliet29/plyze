from utils4plans.logconfig import logset
from datetime import datetime
import altair as alt

from cyclopts import App

from plys.jpg.main import idf_to_jpgraph, set_levels
from plys.utils import CaseData
from plys.paths import ProjectPaths
from plys.qoi.bivar_plots import bivar_plot, multi_bivar_plot
from plys.qoi.data import to_multi_data
from plys.qoi.plots import (
    corr_plot,
    surface_corr_plot,
    surface_qois,
    to_dataframe_with_spaces,
    zone_qois,
)
from plys.qoi.registry import AltairRenderers, QOIRegistry, QOIandData
from plys.qoi.theme import default_theme
from loguru import logger
import matplotlib.pyplot as plt


app = App()


def keep():
    default_theme()
    logger.debug("")
    plt.plot()


cd = CaseData(ProjectPaths.sample_idf, ProjectPaths.sample_sql)

### ----- DATA --------


def data_create():
    return to_dataframe_with_spaces(
        QOIRegistry.flow_12, ProjectPaths.sample_idf, ProjectPaths.sample_sql
    )


def custom_qoi():
    return to_dataframe_with_spaces(
        QOIRegistry.custom.net_flow, ProjectPaths.sample_idf, ProjectPaths.sample_sql
    )


@app.command()
def multidata():
    df = to_multi_data(
        [
            QOIRegistry.custom.net_vent_heat_gain,
            QOIRegistry.vent_vol,
        ],
        ProjectPaths.sample_idf,
        ProjectPaths.sample_sql,
    )
    return df


@app.command()
def carrier():

    return QOIandData(QOIRegistry.custom.unique_wind_pressure, cd.sql).original_arr


### ------- SINGLE PLOTS


@app.command()
def plot_vol():
    qoid = data_create()
    logger.debug(qoid.dataframe)
    chart = corr_plot(qoid)
    chart.show()


@app.command()
def plot_surfs():
    qoid = custom_qoi()  # data_create()
    logger.debug(qoid.dataframe)

    chart = surface_corr_plot(qoid)
    chart.show()


### ------- MULTI PLOTS
@app.command()
def plot_vol_many():
    c = zone_qois(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
    c.show()


@app.command()
def plot_surfs_many():
    c = surface_qois(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
    c.show()


### ------- BIVAR PLORS
@app.command()
def plot_bivar():
    qois_1 = [
        QOIRegistry.custom.net_vent_heat_gain,
        QOIRegistry.vent_vol,
    ]
    df = to_multi_data(
        qois_1,
        *cd,
    )
    c = bivar_plot(df, *qois_1)
    c.show()


@app.command()
def plot_bivar_multi():
    c = multi_bivar_plot(cd)
    c.show()


### ---- JPG ----


@app.command()
def jpgraph():
    jpg = idf_to_jpgraph(*cd, datetime_=datetime(2017, 7, 1, 12))
    logger.debug(jpg.show())
    set_levels(jpg)
    logger.debug(jpg.show())


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
