import polars as pl
from plys.qoi.data import to_multi_data
from plys.utils import CaseData

import altair as alt
from plys.qoi.plots import facet
from plys.qoi.registry import QOIRegistry, QOIType


def bivar_plot(df: pl.DataFrame, q1: QOIType, q2: QOIType):
    chart = (
        alt.Chart(df)
        .mark_point(filled=False, size=200)
        .encode(
            x=alt.X(f"{q1.nickname}:Q").title(q1.name).scale(zero=False),
            y=alt.Y(f"{q2.nickname}:Q").title(None).scale(zero=False),
            color=alt.Color("display_name").scale(scheme="dark2").title("Rooms"),
        )
    )
    return facet(chart, q2.name)


def multi_bivar_plot(cd: CaseData):
    qp1, qp2 = (
        [QOIRegistry.vent_vol, QOIRegistry.custom.net_vent_heat_gain],
        [
            QOIRegistry.mix_vol,
            QOIRegistry.custom.net_mix_heat_gain,
        ],
    )
    chart = alt.hconcat()
    for qp in [qp1, qp2]:
        df = to_multi_data(qp, *cd)
        chart |= bivar_plot(df, *qp)

    return chart
