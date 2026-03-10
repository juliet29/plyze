# test metrics


from plyze.jpg.metrics import (
    calculate_control_value,
    calculate_mean_depth,
    calculate_relative_asymmetry,
    calculate_total_depth,
)
from plyze.examples.jpg.ostwald11 import VillaAlpha
import pytest
import tempfile
from pathlib import Path


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

    @pytest.mark.xfail(reason="Implementation does not match paper")
    def test_calculate_control_value(self):
        res = calculate_control_value(self.G)
        assert res == self.metrics.control_value

    def test_io(self):
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td) / "out.json"
            self.metrics.write(tpath)
            res = self.metrics.read(tpath)
            assert res.total_depth == self.metrics.total_depth

        # for rk, mk in zip(res.keys(), self.metrics.control_value.keys()):
        #
        #     assert round(res[rk], 2) == self.metrics.control_value[mk]
