# test metrics
import pytest


from plyze.jpg.metrics import (
    calculate_diamond_relative_asymmetry,
    calculate_mean_depth,
    calculate_relative_asymmetry,
    calculate_total_depth,
)
from plyze.examples.jpg.ostwald11 import VillaAlpha
import tempfile
from pathlib import Path

from plyze.jpg.scalable_graphs import determine_node_pairs


class TestMetricsVillaAlpha:
    va = VillaAlpha()
    G = va.graph
    metrics = va.metrics

    def test_calculate_total_depth(self):
        res = calculate_total_depth(self.G)
        assert round(res, 2) == self.metrics.total_depth

    def test_calculate_mean_depth(self):
        res = calculate_mean_depth(self.G, self.metrics.total_depth)
        assert round(res, 2) == self.metrics.mean_depth

    def test_calculate_relative_asymmetry(self):
        res = calculate_relative_asymmetry(self.G, self.metrics.mean_depth)
        assert round(res, 2) == self.metrics.relative_asymmetry

    # @pytest.mark.xfail(reason="Implementation does not match paper")
    # def test_calculate_control_value(self):
    #     res = calculate_control_value(self.G)
    #     assert res == self.metrics.control_value
    #
    def test_io(self):
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td) / "out.json"
            self.metrics.write(tpath)
            res = self.metrics.read(tpath)
            assert res.total_depth == self.metrics.total_depth

        # for rk, mk in zip(re.keys(), self.metrics.control_value.keys()):
        #
        #     assert round(res[rk], 2) == self.metrics.control_value[mk]
        #
        #


class TestPyramidScalableGraph:
    node_pair_tests: list[tuple[int, list[int]]] = [
        (3, [3, 1]),
        (4, [4, 2, 1]),
        (8, [8, 4, 2, 1]),
        (10, [10, 5, 2, 1]),
        (11, [11, 5, 2, 1]),
    ]

    node_pair_tests_ceil: list[tuple[int, list[int]]] = [
        (3, [3, 2, 1]),
        (4, [4, 2, 1]),
        (8, [8, 4, 2, 1]),
        (10, [10, 5, 3, 2, 1]),
        (11, [11, 6, 3, 2, 1]),
    ]

    @pytest.mark.parametrize("k, expected_node_nums", node_pair_tests_ceil)
    def test_node_pairs(self, k, expected_node_nums):
        node_nums, _ = determine_node_pairs(k)
        assert node_nums == expected_node_nums

    ra_tests: list[tuple[int, float]] = [
        (5, 0.352),
        (8, 0.328),
        (10, 0.306),
        (11, 0.295),
    ]

    @pytest.mark.parametrize("k, expected_ra", ra_tests)
    def test_ra(self, k, expected_ra):
        ra = calculate_diamond_relative_asymmetry(
            k,
        )
        assert ra == expected_ra
