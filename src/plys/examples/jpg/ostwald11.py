from plys.jpg.interfaces import JPGraph, JPNodeData, JPNode, JPGMetrics


class VillaAlpha:
    nodes = [
        JPNode("entry", JPNodeData(is_carrier=True, level=0)),
        JPNode("A", JPNodeData(level=1)),
        JPNode("B", JPNodeData(level=2)),
        JPNode("C", JPNodeData(level=5)),
        JPNode("D", JPNodeData(level=4)),
        JPNode("E", JPNodeData(level=3)),
        JPNode("F", JPNodeData(level=2)),
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
        G = JPGraph()
        G.add_jpnodes(self.nodes)
        G.add_edges_from(self.edges)
        return G

    @property
    def metrics(self):
        return JPGMetrics(
            total_depth=17,
            mean_depth=2.83,
            relative_asymmetry=0.73,
            control_value={"entry": 0.33, "A": 2.5, "B": 0.33, "F": 0.83},
        )
