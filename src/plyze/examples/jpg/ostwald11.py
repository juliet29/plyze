from plyze.jpg.interfaces import JPGraph, JPNodeData, JPNode, JPGMetrics


class VillaAlpha:
    graph_name = "ostwald11_villa_alpha"
    nodes = [
        JPNode(name="entry", data=JPNodeData(is_carrier=True, level=0)),
        JPNode(name="A", data=JPNodeData(level=1)),
        JPNode(name="B", data=JPNodeData(level=2)),
        JPNode(name="C", data=JPNodeData(level=5)),
        JPNode(name="D", data=JPNodeData(level=4)),
        JPNode(name="E", data=JPNodeData(level=3)),
        JPNode(name="F", data=JPNodeData(level=2)),
    ]

    edges = [
        ("entry", "A"),
        ("A", "F"),
        ("F", "E"),
        ("E", "D"),
        ("D", "C"),
    ]

    @property
    def graph(self):
        return JPGraph.create(self.graph_name, self.nodes, self.edges)

    @property
    def metrics(self):
        return JPGMetrics(
            graph_name=self.graph_name,
            total_depth=17,
            mean_depth=2.83,
            relative_asymmetry=0.73,
            control_value={"entry": 0.33, "A": 2.5, "B": 0.33, "F": 0.83},
        )
