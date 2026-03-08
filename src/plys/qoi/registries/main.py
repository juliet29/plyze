from plys.qoi.registries.interfaces import EpQOI
from plys.qoi.registries.custom_qois import CustomQOIRegistry


class QOIRegistry:
    custom = CustomQOIRegistry
    flow_12 = EpQOI(
        "AFN Linkage Node 1 to Node 2 Volume Flow Rate", "net_flow", "m3/s", "Surface"
    )
    flow_21 = EpQOI(
        "AFN Linkage Node 2 to Node 1 Volume Flow Rate", "net_flow", "m3/s", "Surface"
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
