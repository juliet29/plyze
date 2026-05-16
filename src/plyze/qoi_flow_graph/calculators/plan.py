from dataclasses import dataclass
import xarray as xr
from plyze.flow_graph.interfaces import FlowGraph
from plyze.qoi_flow_graph.registry import GraphQOIRegistry
from plyze.qoi_flow_graph.interfaces import (
    GraphQOIBaseCalculator,
)
from plyze.utils import XArrayNames


@dataclass()
class PlanQOICalculator(GraphQOIBaseCalculator):
    G: FlowGraph

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
        return GraphQOIRegistry.zone_inflow.fx(flows)

    @property
    def outflow(self):
        if not self.ventilating_surfaces:
            return self.empty_data
        flows = [i.data.flow_out for i in self.ventilating_surfaces]
        return GraphQOIRegistry.zone_outflow.fx(flows)

    @property
    def flow_diff(self):
        return GraphQOIRegistry.plan_flow_loss.fx(
            inflow=self.inflow, outflow=self.outflow
        )

    def pressure_diff(self):
        # may need to do more work on the function side.. -> need to return all four sides, and then find the max and min..
        pressure_data = [i.data.external_wind_pressure for i in self.G.external_nodes]
        return GraphQOIRegistry.plan_max_pressure_diff.fx(pressure_data)

    def make_registers(self):
        self.register(GraphQOIRegistry.zone_inflow, self.inflow)
        self.register(GraphQOIRegistry.zone_outflow, self.outflow)
        self.register(GraphQOIRegistry.plan_flow_loss, self.flow_diff)

    def run(self):
        self.calculate([self.make_registers])
