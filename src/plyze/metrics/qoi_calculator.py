# TODO: delete will be replaced by flow_graph_qoi/graph_qoi.py
from dataclasses import dataclass
import xarray as xr
from plyze.metrics.registries import MetricRegistry
from plyze.qoi_flow_graph.zone_data import (
    create_flow_graph_xarray,
)
from plyze.qoi_flow_graph.dim_zone_data import (
    EnvironmentalComparisons,
    make_enviro_norm_data,
)
from plyze.utils import XArrayNames
from plyze.qoi.xarray_helpers import get_single_value

from plyze.metrics.interfaces import BaseCalculator
from plyze.flow_graph.interfaces import ZoneNodeQOINames


QMR = MetricRegistry.qoi


def get_space_time_median(arr: xr.DataArray):
    return get_single_value(arr.median(dim=XArrayNames.SPACE).median())


@dataclass
class SpaceTimeQOICalculator(BaseCalculator):
    enviro: EnvironmentalComparisons

    def compute_median_values(self, zone_qoi: ZoneNodeQOINames):
        plan_data = create_flow_graph_xarray(
            lambda x: x.data.get_qoi_array(zone_qoi), self.G.zone_nodes
        )
        return get_space_time_median(plan_data)

    def calc_median_values_all_qoi(self):
        self.register(QMR.median_mix_vol, self.compute_median_values("mixing_volume"))
        self.register(
            QMR.median_vent_vol, self.compute_median_values("ventilation_volume")
        )
        self.register(QMR.median_temp, self.compute_median_values("temperature"))

    def calc_median_values_env_qoi(self):
        norm_arrays = make_enviro_norm_data(self.G, self.enviro)
        medians = [get_space_time_median(i) for i in norm_arrays]
        self.register(QMR.median_norm_mix_vol, medians[0])
        self.register(QMR.median_norm_vent_vol, medians[1])
        self.register(QMR.median_norm_temp, medians[2])
        self.register(QMR.median_norm_temp_no_scale, medians[3])

    def run(self):
        return self.calculate(
            [self.calc_median_values_all_qoi, self.calc_median_values_env_qoi]
        )
