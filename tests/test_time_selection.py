from plyze.qoi.data.data import TimeSelection


def test_time_select_creation():
    ts = TimeSelection(2017, [1], [1, 2], [1, 2], listwise=False)
    res = ts.calc_datetimes()
    assert len(res) == 4


def test_time_selection_without_specific_hours():
    ts = TimeSelection(2017, [1], [1], [], listwise=False)
    res = ts.calc_datetimes()
    assert len(res) == 24


def test_time_selection_listwise():
    ts = TimeSelection(2017, [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], listwise=True)
    res = ts.calc_datetimes()
    assert len(res) == 4
