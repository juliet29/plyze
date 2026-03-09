from pathlib import Path

from loguru import logger

from plys.qoi.data.outputs import gather_standard_data
from cyclopts import App


qoi = App(name="qoi")


@qoi.command()
def create(
    case_name: str, idf_path: Path, sql_path: Path, zonal_path: Path, surface_path: Path
):
    dfs = gather_standard_data(idf_path, sql_path, case_name)
    dfs.zonal.config_meta.write_parquet(zonal_path)
    dfs.surface.config_meta.write_parquet(surface_path)
    logger.debug("Finished writing standard data")


@qoi.command()
def consolidate(data_paths: list[Path], csv_path: Path):
    pass
