from datetime import datetime
from pathlib import Path

from plys.jpg.metrics import calculate_jpg_metrics
from plys.jpg.main import idf_to_jpgraph


def create_jpg(idf_path: Path, sql_path: Path, datetime_: datetime, jpg_path: Path):
    # TODO: datetime will come from a config file
    G = idf_to_jpgraph(idf_path, sql_path, datetime_)
    G.write(jpg_path)
    logger.success("Finished writing JPG")


def create_jpg_metrics(jpg_path: Path, metrics_path: Path):
    G = read_jpg(jpg_path)
    metrics = calculate_jpg_metrics(G)
    metrics.write(metrics_path)
    logger.success("Finished writing JPG metrics")
