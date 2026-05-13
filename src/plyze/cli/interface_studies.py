from cyclopts import App

from plyze.qoi.data.data import TimeSelection

app = App()


@app.command
def test_timeselect():
    ts = TimeSelection(
        2010,
        [
            1,
            2,
        ],
        [1, 2],
        [1, 2],
        listwise=True,
    )
    return ts.calc_datetimes()
