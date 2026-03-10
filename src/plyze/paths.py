from pathlib import Path
import pyprojroot


BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))


class StaticPaths:
    base = Path(BASE_PATH) / "static"
    inputs = base / "1_inputs"
    temp = base / "4_temp"


class ProjectPaths:
    sample_xarray = StaticPaths.inputs / "msd/data.nc"
    sample_sql = StaticPaths.inputs / "msd/eplusout.sql"
    sample_idf = StaticPaths.inputs / "msd/run.idf"
