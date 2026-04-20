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


class MetricRegistry:
    flow = FlowMetricRegistry
    plan = PlanMetricRegistry
