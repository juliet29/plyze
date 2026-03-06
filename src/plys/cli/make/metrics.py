from datetime import datetime
import polars as pl
from pathlib import Path

from plys.jpg.interfaces import JPGMetrics, JPGraphModel
from plys.jpg.metrics import calculate_jpg_metrics
from plys.jpg.main import idf_to_jpgraph
from loguru import logger


def create_jpg(idf_path: Path, sql_path: Path, date_time: datetime, jpg_path: Path):
    """
    Datetime format must be %Y-%m-%dT%H:%M:%. See [cyclopts rules on coercing dates](https://cyclopts.readthedocs.io/en/latest/rules.html#datetime)
    """
    # TODO: datetime will come from a config file
    G = idf_to_jpgraph(idf_path, sql_path, date_time)
    JPGraphModel.write(G, jpg_path)
    logger.success("Finished writing JPG")


def create_jpg_metrics(jpg_path: Path, metrics_path: Path):
    G = JPGraphModel.read(jpg_path)
    metrics = calculate_jpg_metrics(G)
    metrics.write(metrics_path)
    logger.success("Finished writing JPG metrics")


def consolidate_cases_jpg_metrics(
    metrics_paths: list[Path], case_names: list[str], csv_path: Path
):
    # TODO: make sure the paths and string names are aligned!
    all_metrics = [JPGMetrics.read(i) for i in metrics_paths]
    df = pl.DataFrame(all_metrics).with_columns(case=case_names)
    df.write_csv(csv_path)
    logger.success("Finished consolidating JPG metrics")
