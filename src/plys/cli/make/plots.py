from plys.paths import ProjectPaths
from plys.qoi.plots import (
    corr_plot,
    surface_corr_plot,
    surface_qois,
    to_dataframe_with_spaces,
    zone_qois,
)
from plys.qoi.registry import QOIType
from pathlib import Path

### ------- DESIGN METRICS  ---------------------- #####

### ------- QUANTITIES OF INTEREST ---------------------- #####
### ------- SINGLE PLOTS


def plot_vol(qoi: QOIType, idf_path: Path, sql_path: Path):
    qoid = to_dataframe_with_spaces(qoi, idf_path, sql_path)
    chart = corr_plot(qoid)
    chart.show()


def plot_surface(qoi: QOIType, idf_path: Path, sql_path: Path):

    qoid = to_dataframe_with_spaces(qoi, idf_path, sql_path)

    chart = surface_corr_plot(qoid)
    chart.show()


### ------- MULTI PLOTS


def plot_vol_many():
    c = zone_qois(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
    c.show()


def plot_surf_many():
    c = surface_qois(ProjectPaths.sample_idf, ProjectPaths.sample_sql)
    c.show()
