from datetime import datetime
import polars as pl
from pathlib import Path

from plyze.jpg.interfaces import JPGMetrics, JPGraphModel
from plyze.jpg.metrics import calculate_jpg_metrics
from plyze.jpg.main import idf_to_jpgraph
from loguru import logger
from cyclopts import App


jpg = App(name="jpg")


@jpg.command()
def create(
    graph_name: str, idf_path: Path, sql_path: Path, date_time: datetime, jpg_path: Path
):
    """
    Datetime format must be %Y-%m-%dT%H:%M:%.
    See [cyclopts rules on coercing dates](https://cyclopts.readthedocs.io/en/latest/rules.html#datetime)
    """
    # TODO: register datetime as help!, not function description
    G = idf_to_jpgraph(graph_name, idf_path, sql_path, date_time)
    JPGraphModel.write(G, jpg_path)
    logger.success("Finished writing JPG")


@jpg.command()
def create_metrics(jpg_path: Path, metrics_path: Path):
    G = JPGraphModel.read(jpg_path)
    metrics = calculate_jpg_metrics(G)
    metrics.write(metrics_path)
    logger.success("Finished writing JPG metrics")


@jpg.command()
def consolidate(metrics_paths: list[Path], csv_path: Path):
    # TODO: make sure the paths and string names are aligned!
    logger.debug(metrics_paths)
    all_metrics = [JPGMetrics.read(i) for i in metrics_paths]
    logger.debug(all_metrics)
    df = pl.DataFrame(all_metrics)
    df.write_csv(csv_path)
    logger.success("Finished consolidating JPG metrics")
