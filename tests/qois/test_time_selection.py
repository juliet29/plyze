from plyze.qoi.data.data import TimeSelection


def test_time_select_creation():
    ts = TimeSelection(2017, 1, [1, 2], [1, 2])
    res = ts.calc_datetimes()
    assert len(res) == 4


def test_time_selection_without_specific_hours():
    ts = TimeSelection(2017, 1, [1], [])
    res = ts.calc_datetimes()
    assert len(res) == 24
