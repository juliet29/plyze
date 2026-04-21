from dataclasses import dataclass
from plyze.metrics.registries import MetricRegistry
from plyze.qoi_flow_graph.zone_data import create_flow_graph_xarray
from plyze.utils import XArrayNames
from plyze.qoi.xarray_helpers import get_single_value

from plyze.metrics.interfaces import BaseCalculator
from plyze.flow_graph.interfaces import ZoneNodeQOINames


QMR = MetricRegistry.qoi


@dataclass
class SpaceTimeQOICalculator(BaseCalculator):
    pass

    def compute_median_values(self, zone_qoi: ZoneNodeQOINames):
        plan_data = create_flow_graph_xarray(
            lambda x: x.data.get_qoi_array(zone_qoi), self.G.zone_nodes
        )

        # plan_data = xr.concat(
        #     [i.data.get_qoi_array(zone_qoi) for i in self.G.zone_nodes],
        #     dim=XArrayNames.SPACE,
        # )
        return get_single_value(plan_data.median(dim=XArrayNames.SPACE).median())

    def calc_median_values_all_qoi(self):
        self.register(QMR.median_mix_vol, self.compute_median_values("mixing_volume"))
        self.register(
            QMR.median_vent_vol, self.compute_median_values("ventilation_volume")
        )
        self.register(QMR.median_temp, self.compute_median_values("temperature"))

    def run(self):
        return self.calculate([self.calc_median_values_all_qoi])
