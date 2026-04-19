from plyze.flow_graph.interfaces import (
    ZoneNodeData,
    ZoneNode,
)

from plan2eplus.ezcase.ez import EZ
from plan2eplus.ops.zones.ezobject import Zone


from plan2eplus.geometry.domain import Domain
from plan2eplus.geometry.ortho_domain import OrthoDomain


def calculate_domain_aspect_ratio(
    domain: OrthoDomain | Domain,
):  # TODO: implement on the class, especially OrthoDomain, and clean up duplication!
    if isinstance(domain, Domain):
        return domain.horz_range.size / domain.vert_range.size
    return (
        domain.bounding_domain.horz_range.size / domain.bounding_domain.vert_range.size
    )


def make_zone_from_node(zone: Zone):

    domain = zone.domain

    # TODO: determine if room is in AFN.. but skip this metric for now..

    return ZoneNode(
        zone.room_name,
        data=ZoneNodeData(
            location=domain.centroid,
            area=domain.area,
            aspect_ratio=calculate_domain_aspect_ratio(domain),
            is_in_afn=False,
            # vent_volume=get_space_arr(ventilation_volume, zone_name),
            # mix_volume=get_space_arr(mixing_volume, zone_name),
            # ach=get_space_arr(ach, zone_name),
        ),
    )


def make_zones_for_graph(case: EZ):
    zone_nodes = case.objects.zones
    zones = [make_zone_from_node(i) for i in zone_nodes]
    return zones
