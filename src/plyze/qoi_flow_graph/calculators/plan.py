from dataclasses import dataclass
import xarray as xr
from plyze.flow_graph.interfaces import AmbientData, FlowGraph
from plyze.qoi_flow_graph.registry import GraphQOIRegistry
from plyze.qoi_flow_graph.interfaces import (
    GraphQOIBaseCalculator,
    GraphQOIHolder,
)
from plyze.utils import XArrayNames


@dataclass()
class PlanQOICalculator(GraphQOIBaseCalculator):
    G: FlowGraph
    ambient_data: AmbientData

    @property
    def empty_data(self):
        zone = self.G.zone_nodes[0]
        return xr.zeros_like(zone.data.temperature)

    @property
    def ventilating_surfaces(self):
        """Consider windows to be the ventilating_surfaces"""
        return [i for i in self.G.edges_with_data if i.data.surface_type == "Window"]

    @property
    def inflow(self):
        if not self.ventilating_surfaces:
            return self.empty_data
        flows = [
            i.data.flow_in.drop_vars(XArrayNames.SPACE)
            for i in self.ventilating_surfaces
        ]
        return GraphQOIRegistry.plan_inflow.fx(flows).drop_duplicates(
            dim=XArrayNames.DATETIME
        )

    @property
    def outflow(self):
        if not self.ventilating_surfaces:
            return self.empty_data
        flows = [i.data.flow_out for i in self.ventilating_surfaces]
        return GraphQOIRegistry.plan_outflow.fx(flows).drop_duplicates(
            dim=XArrayNames.DATETIME
        )

    @property
    def flow_diff(self):
        return GraphQOIRegistry.plan_flow_loss.fx(
            inflow=self.inflow, outflow=self.outflow
        )

    @property
    def dimless_flow(self):
        surface_areas = [i.data.surface_area for i in self.ventilating_surfaces]
        wind = self.ambient_data.wind_speed
        inflow = self.inflow
        inflow.name = "inflow"

        res = xr.merge(
            [inflow, wind],
        )
        return GraphQOIRegistry.plan_dimless_inflow.fx(
            wind_speed=res.wind_speed,
            zone_sum_flow=res.inflow,
            surface_areas=surface_areas,
        )

    def pressure_diff(self):
        # may need to do more work on the function side.. -> need to return all four sides, and then find the max and min..
        pressure_data = [i.data.external_wind_pressure for i in self.G.external_nodes]
        return GraphQOIRegistry.plan_max_pressure_diff.fx(pressure_data)

    def make_registers(self):
        self.register(GraphQOIRegistry.plan_inflow, self.inflow)
        self.register(GraphQOIRegistry.plan_outflow, self.outflow)
        self.register(GraphQOIRegistry.plan_flow_loss, self.flow_diff)
        self.register(GraphQOIRegistry.plan_dimless_inflow, self.dimless_flow)

    def run(self):
        self.calculate([self.make_registers])


def make_plan_qois(G: FlowGraph, ambient_data: AmbientData):
    holder = GraphQOIHolder()
    pq = PlanQOICalculator(holder, "", G, ambient_data)
    pq.run()
    return holder
