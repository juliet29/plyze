from pathlib import Path
import polars as pl
import tempfile
from plyze.examples.casedata import example_casedata
from plyze.examples.time_selection import EXAMPLE_TIME_SELECTION
from plyze.cli.make.qoi import create
from plyze.qoi.data.interfaces import CaseQOIandData
from plyze.qoi.data.outputs import consolidate_data, get_surface_qois


def test_gather_standard_data():
    case_name = "example"
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        zp = tdir / "zonal.parquet"
        sp = tdir / "surface.parquet"
        create(case_name, *example_casedata, zp, sp, EXAMPLE_TIME_SELECTION)
        # TODO: test read and write methods explicitly
        assert pl.read_parquet_metadata(zp)["case_name"] == case_name


def test_consolidating_data():
    df1 = get_surface_qois(*example_casedata, EXAMPLE_TIME_SELECTION)
    df2 = get_surface_qois(*example_casedata, EXAMPLE_TIME_SELECTION)
    case_names = ["c1", "c2"]
    case_datas = [CaseQOIandData(case, df) for case, df in zip(case_names, [df1, df2])]
    df = consolidate_data(case_datas)
    assert sorted(df["case_name"].unique().to_list()) == sorted(case_names)
