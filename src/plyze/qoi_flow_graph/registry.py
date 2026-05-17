from plyze.qoi_flow_graph.interfaces import GraphQOI
from plyze.qoi_flow_graph.functions import (
    inflow,
    outflow,
    dimless_flow,
    zone_dimless_temp,
    plan_flow_loss,
    plan_max_pressure_diff,
)


class GraphQOIRegistry:
    zone_inflow = GraphQOI(
        "zone_inflow",
        "zone_inflow",
        unit="m3/s",
        space_type="Zone",
        fx=inflow,
    )
    zone_outflow = GraphQOI(
        "zone_outflow", "zone_outflow", unit="m3/s", space_type="Zone", fx=outflow
    )

    zone_dimless_flow = GraphQOI(
        "zone_dimless_flow",
        "zone_dimless_flow",
        unit="",
        space_type="Zone",
        fx=dimless_flow,
    )

    zone_dimless_temp = GraphQOI(
        "zone_dimless_temp",
        "zone_dimless_temp",
        unit="",
        space_type="Zone",
        fx=zone_dimless_temp,
    )

    plan_inflow = GraphQOI(
        "plan_inflow",
        "plan_inflow",
        unit="m3/s",
        space_type="Plan",
        fx=inflow,
    )
    plan_dimless_inflow = GraphQOI(
        "plan_dimless_inflow",
        "plan_dimless_inflow",
        unit="m3/s",
        space_type="Plan",
        fx=dimless_flow,
    )

    plan_outflow = GraphQOI(
        "plan_outflow",
        "plan_outflow",
        unit="m3/s",
        space_type="Plan",
        fx=outflow,
    )

    plan_flow_loss = GraphQOI(
        "plan_flow_loss",
        "plan_flow_loss",
        unit="m3/s",
        space_type="Plan",
        fx=plan_flow_loss,
    )

    plan_max_pressure_diff = GraphQOI(
        "plan_max_pressure_diff",
        "plan_max_pressure_diff",
        unit="m3/s",
        space_type="Plan",
        fx=plan_max_pressure_diff,
    )
