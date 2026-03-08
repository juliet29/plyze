import polars as pl
from pathlib import Path
import altair as alt
from plys.qoi.registry import QOIRegistry, QOIandData

from plys.qoi.data import to_dataframe_with_spaces


def plot_setup(qoidata: QOIandData):
    assert isinstance(
        qoidata.dataframe, pl.DataFrame
    ), f"Expected a dataframe, instead got: {qoidata.dataframe}. "
    chart = (
        alt.Chart(
            qoidata.dataframe,
        )
        .mark_point(filled=True, size=200)
        .encode(
            x=alt.X("area:Q").title("Area [m]").scale(zero=False),
            y=alt.Y(f"{qoidata.qoi.nickname}:Q").title(None).scale(zero=False),
            color=alt.Color("display_name").scale(scheme="dark2").title("Rooms"),
        )
    )
    return chart


def facet(chart: alt.Chart, label: str):
    return chart.properties(width=200, height=100).facet(
        # TODO: put this in "Metrics" registry..
        column=alt.Column("monthdate(datetimes):T").title(None),
        row=alt.Row("hours(datetimes):T").title(label),
    )


def corr_plot(qoidata: QOIandData):
    return facet(plot_setup(qoidata), qoidata.qoi.label)


def surface_corr_plot(qoidata: QOIandData):
    chart = (
        plot_setup(qoidata)
        .mark_point(filled=False, size=200)
        .encode(
            x=alt.X("direction").title("Direction"),
            color=alt.Color("zone_display_name:N")
            .sort()
            .scale(scheme="dark2")
            .title("Rooms Corresponding to Surface"),
            shape=alt.Shape("type_"),
            fill=alt.condition(
                "datum.type_ == 'Window'",
                alt.Color("zone_display_name:N").sort().scale(scheme="dark2"),
                alt.value("transparent"),
            ),
        )
    )
    return facet(chart, qoidata.qoi.label)


def zone_qois(idf: Path, sql: Path):
    qois = [
        QOIRegistry.temp,
        QOIRegistry.vent_vol,
        QOIRegistry.vent_heat_gain,
        QOIRegistry.vent_heat_loss,
        QOIRegistry.mix_vol,
        QOIRegistry.mix_heat_gain,
        QOIRegistry.mix_heat_loss,
    ]
    charts = [corr_plot(to_dataframe_with_spaces(i, idf, sql)) for i in qois]
    chart = charts[0] | charts[1]
    for c in charts[2:]:
        chart |= c
    return chart


def surface_qois(idf: Path, sql: Path):
    qois = [
        QOIRegistry.flow_12,
        QOIRegistry.flow_21,
    ]

    charts = [surface_corr_plot(to_dataframe_with_spaces(i, idf, sql)) for i in qois]
    chart = charts[0] | charts[1]
    return chart
