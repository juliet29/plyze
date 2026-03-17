from plyze.qoi.registries.interfaces import EpQOI
from plyze.qoi.registries.custom import CustomQOIRegistry


class SiteQOIRegistry:
    temp = EpQOI("Site Outdoor Air Drybulb Temperature", "tout", "ºC", "Site")
    wind_speed = EpQOI("Site Wind Speed", "wind_speed", "m/s", "Site")
    wind_direction = EpQOI("Site Wind Direction", "wind_direction", "º", "Site")

    all = [temp, wind_speed, wind_direction]
    # TODO: on next E+ cration record the solar radiation
    # solar_rad = EpQOI("Solar Radiation", "tout", "ºC", "Site")


class QOIRegistry:
    custom = CustomQOIRegistry
    site = SiteQOIRegistry
    flow_out = EpQOI(
        "AFN Linkage Node 1 to Node 2 Volume Flow Rate",
        "flow_out",
        "m3/s",
        "Surface",
        info="~Outgoing flows~: Outdoor flows: from thermal zone to outdoors. Indoor flows: from thermal zone 'owning' the surface to its neighbor.",
    )
    flow_in = EpQOI(
        "AFN Linkage Node 2 to Node 1 Volume Flow Rate",
        "flow_in",
        "m3/s",
        "Surface",
        info="~Incoming flows~: From outdoors to the thermal zone, from neighbors sharing surface to THIS zone (which `owns` the surface)",
    )

    temp = EpQOI("Zone Mean Air Temperature", "temp", "C", "Zone")
    mix_vol = EpQOI("AFN Zone Mixing Volume", "mix_vol", "m3", "Zone")
    vent_vol = EpQOI("AFN Zone Ventilation Volume", "vent_vol", "m3", "Zone")

    mix_heat_gain = EpQOI(
        "AFN Zone Mixing Sensible Heat Gain Rate",
        "mix_heat_gain",
        "W",
        "Zone",
    )
    vent_heat_gain = EpQOI(
        "AFN Zone Ventilation Sensible Heat Gain Rate",
        "vent_heat_gain",
        "W",
        "Zone",
    )

    mix_heat_loss = EpQOI(
        "AFN Zone Mixing Sensible Heat Loss Rate",
        "mix_heat_loss",
        "W",
        "Zone",
    )
    vent_heat_loss = EpQOI(
        "AFN Zone Ventilation Sensible Heat Loss Rate",
        "vent_heat_loss",
        "W",
        "Zone",
    )
    wind_pressure = EpQOI(
        "AFN Node Wind Pressure",
        "wind_pressure",
        "Pa",
        "System",
    )

    zonal_features = [
        temp,
        mix_vol,
        vent_vol,
        vent_heat_gain,
        vent_heat_loss,
        mix_heat_gain,
        mix_heat_loss,
        custom.net_vent_heat_gain,
        custom.net_mix_heat_gain,
    ]

    zonal_feature_nicknames = [i.nickname for i in zonal_features]
