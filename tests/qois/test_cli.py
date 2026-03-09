from pathlib import Path
import polars as pl
import tempfile
from plys.examples.casedata import ex
from plys.cli.make.qoi import create
from plys.qoi.data.interfaces import CaseQOIandData
from plys.qoi.data.outputs import consolidate_data, get_surface_qois


def test_gather_standard_data():
    case_name = "example"
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        zp = tdir / "zonal.parquet"
        sp = tdir / "surface.parquet"
        create(case_name, *ex, zp, sp)
        # TODO: test read and write methods explicitly
        assert pl.read_parquet_metadata(zp)["case_name"] == case_name


def test_consolidating_data():
    df1 = get_surface_qois(*ex)
    df2 = get_surface_qois(*ex)
    case_names = ["c1", "c2"]
    case_datas = [CaseQOIandData(case, df) for case, df in zip(case_names, [df1, df2])]
    df = consolidate_data(case_datas)
    assert df["case_name"].unique().to_list() == case_names
