from plyze.qoi.xarray_helpers import find_drn_in_name
from utils4plans.lists import sort_and_group_objects
from pathlib import Path
from plan2eplus.results.sql import get_qoi
from plyze.qoi.registries.interfaces import CustomQOIComponents, CustomQOI

# hello
# @dataclass(frozen=True)
# class OutgoingFlow(GenericQOI):
#     name: str
#
#     def fx(self, sql_path: Path):
#         # arr_a = get_qoi(self.components.a, sql_path).data_arr
#         # need to combine all outgoing flows for a zone and change space names to be zones..
#         # so here would need the space idfs...
#         # this could potentially alter the dag...
#         pass


# OTHER FUNCTIONS --- > Modifying the xarray dataarray in some more complex way...
def get_zone_total_incoming_flow(sql_path: Path):
    f21 = get_qoi("AFN Linkage Node 2 to Node 1 Volume Flow Rate", sql_path).data_arr
    # don't want to rely on the IDF, so use the zone temperatures to get the zone names and group together..
    pass


def get_wind_pressure_unique_external_nodes(sql_path: Path):
    wind_pressure = get_qoi("AFN Node Wind Pressure", sql_path).data_arr

    grouped_space_names = sort_and_group_objects(
        wind_pressure.space_names.to_series().to_list(), lambda x: find_drn_in_name(x)
    )
    # just want the first from each group
    selected_space_names = [i[0] for i in grouped_space_names]
    # TODO: good opportunity to simplify the names..  to be the direction..
    # TODO: this should happen here and not in the jpg
    return wind_pressure.sel(space_names=selected_space_names)


class CustomQOIRegistry:
    net_out_flow = CustomQOI(  # NOTE: this is really more of a dissipation metric..
        name="AFN Linkage Node 1 to Node 2 Net Volume Flow Rate ",
        components=CustomQOIComponents(
            "AFN Linkage Node 1 to Node 2 Volume Flow Rate",
            "AFN Linkage Node 2 to Node 1 Volume Flow Rate",
        ),
        nickname="net_out_flow",
        unit="m3/s",
        space_type="Surface",
        info="Net OUTgoing flow",
    )
    combined_volume = CustomQOI(
        name="AFN Combined Mixing and Ventilation Volume",
        components=CustomQOIComponents(
            "AFN Zone Mixing Volume",
            "AFN Zone Ventilation Volume",
        ),
        operation="+",
        nickname="combined_volume",
        unit="m3",
        space_type="Zone",
    )
    net_vent_heat_gain = CustomQOI(
        name="AFN Zone Ventilation Net Sensible Heat Gain Rate",
        components=CustomQOIComponents(
            "AFN Zone Ventilation Sensible Heat Gain Rate",
            "AFN Zone Ventilation Sensible Heat Loss Rate",
        ),
        nickname="net_vent_heat_gain",
        unit="W",
        space_type="Zone",
    )
    net_mix_heat_gain = CustomQOI(
        name="AFN Zone Mixing Net Sensible Heat Gain Rate",
        components=CustomQOIComponents(
            "AFN Zone Mixing Sensible Heat Gain Rate",
            "AFN Zone Mixing Sensible Heat Loss Rate",
        ),
        nickname="net_mix_heat_gain",
        unit="W",
        space_type="Zone",
    )
    unique_wind_pressure = CustomQOI(
        name="AFN Facade External Node Wind Pressure",
        nickname="unique_wind_pressure",
        unit="Pa",
        space_type="System",
        fx=get_wind_pressure_unique_external_nodes,
    )
