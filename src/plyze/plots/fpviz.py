from pathlib import Path
from plan2eplus.ezcase.ez import EZ
from plan2eplus.visuals.base.base_plot import BasePlot


def plan_plot(idf: Path, show: bool = True):
    case = EZ(idf)
    bp = (
        BasePlot(case.objects.zones)
        .plot_zones()
        .plot_zone_names()
        .plot_subsurfaces_and_surfaces(
            case.objects.airflow_network,
            case.objects.airboundaries,
            case.objects.subsurfaces,
        )
        .plot_cardinal_names()
        .plot_connections(
            case.objects.airflow_network,
            case.objects.airboundaries,
            case.objects.subsurfaces,
        )
        #
    )
    if show:
        bp.show()
