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

    sample_flow_graph_dir = StaticPaths.temp / "flow_graph"
    sample_flow_graph_json = sample_flow_graph_dir / "out.json"
