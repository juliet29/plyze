from plyze.metrics.interfaces import Metric


class PlanMetricRegistry:
    area = Metric("area", "Area [m2]")
    num_rooms = Metric("num_rooms", "Number of Rooms")


class FlowMetricRegistry:
    num_paths = Metric("num_paths", "Number of Paths")
    avg_path_length = Metric("avg_path_length", "Average Length of Paths")
    mode_path_length = Metric("mode_path_length", "Most Frequent Length of Paths")
    len_shortest_path = Metric("len_shortest_path", "Length of Shortest Path")
    degree_dom_node = Metric("degree_dom_node", "Degree of Dominant Node")

    dominant_node_direction = Metric(
        "dominant_node_direction", "Direction of Dominant Node"
    )
    mean_depth_dom_node = Metric("mean_depth_dom_node", "Mean Depth of Dominant Node")


class QOIMetricRegistry:
    median_temp = Metric("median_temp", "Space and Time Median Temperature")
    median_mix_vol = Metric("median_mix_vol", "Space and Time Median Mixing Volume")
    median_vent_vol = Metric(
        "median_vent_vol", "Space and Time Median Ventilation Volume"
    )

    median_norm_vent_vol = Metric(
        "median_norm_vent_vol", "Space and Time Median Ventilation Volume"
    )
    median_norm_mix_vol = Metric(
        "median_norm_mix_vol", "Space and Time Median Mixing Volume"
    )
    median_norm_temp = Metric("median_norm_temp", "Space and Time Median Temperature")
    median_norm_temp_no_scale = Metric(
        "median_norm_temp_no_scale", "Space and Time Median Temperature (No Scale)"
    )


class MetricRegistry:
    flow = FlowMetricRegistry
    plan = PlanMetricRegistry
