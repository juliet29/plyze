from dataclasses import dataclass
import xarray as xr
from plyze.flow_graph.interfaces import AmbientData, FlowGraph, ZoneNode
from plyze.qoi_flow_graph.graph_qoi_interfaces import (
    GraphQOIBaseCalculator,
    GraphQOIRegistry,
)


@dataclass()
class GraphQOICalculator(GraphQOIBaseCalculator):
    # NOTE: this is calculated on a per-zone level and will be added to the original graph.. which means it merits being added to the original flow_graph folder..; and mybe should do all QOIs this way, not just those that are calculated..
    G: FlowGraph
    zone: ZoneNode
    ambient_data: AmbientData

    @property
    def zone_edges(self):
        # TODO: test that can get the correct edges..
        edges = self.G.get_edges_of_zone(self.zone)
        e = [i for i in self.G.edges_with_data if i in edges]
        return e

    def comp_flow_in(self):
        flow_in_data = [i.data.flow_in for i in self.zone_edges]
        if not self.zone_edges:
            return xr.zeros_like(self.ambient_data.t_out)
        return GraphQOIRegistry.zone_inflow.fx(flow_in_data)

    # TODO: make sure this function returns a data array -> check that inputs are aligned on the other edges => should all have the same datatime reporting.. may have to cllapse space metrics

    def comp_flow_out(self):
        flow_out_data = [i.data.flow_out for i in self.zone_edges]
        if not self.zone_edges:
            return xr.zeros_like(self.ambient_data.t_out)
        return GraphQOIRegistry.zone_outflow.fx(flow_out_data)

    def calculate_zone_accum_flow(self):
        self.register(GraphQOIRegistry.zone_inflow, self.comp_flow_in())

        self.register(GraphQOIRegistry.zone_outflow, self.comp_flow_out())

    def calculate_dimensionless(self):
        in_flow = self.comp_flow_in()
        surface_areas = [i.data.surface_area for i in self.zone_edges]

        self.register(
            GraphQOIRegistry.zone_dimless_flow,
            GraphQOIRegistry.zone_dimless_flow.fx(
                self.ambient_data.wind_speed, in_flow, surface_areas
            ),
        )

        self.register(
            GraphQOIRegistry.zone_dimless_temp,
            GraphQOIRegistry.zone_dimless_temp.fx(
                self.ambient_data.t_out, self.zone.data.temperature
            ),
        )

    def run(self):
        self.calculate([self.calculate_zone_accum_flow, self.calculate_dimensionless])
