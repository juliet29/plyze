from sklearn.neighbors import NearestNeighbors
import altair as alt
import polars as pl
from sklearn.cluster import SpectralClustering
import numpy as np


# NEAREST NEIGBORS
def fit_neighbors(samples: np.ndarray, n: int):
    model = NearestNeighbors(n_neighbors=n)
    model.fit(samples)
    return model


def show_neighbors_one(model: NearestNeighbors, sample: np.ndarray):
    return model.kneighbors(sample)


# SPECTRAL CLUSTERING
def fit_samples(samples: np.ndarray, n_clusters: int):
    model = SpectralClustering(n_clusters=n_clusters).fit(samples)
    return model, model.labels_


def get_num_columns(arr: np.ndarray):
    return np.size(arr, axis=1)


def prep_cluster_df(samples: np.ndarray, labels: list[int], feature_names: list[str]):
    # assert get_num_columns(labels) == 1

    n_features = get_num_columns(samples)
    assert len(feature_names) == n_features

    df = pl.from_numpy(data=samples, schema=feature_names).with_columns(labels=labels)

    return df


def show_clusters(df: pl.DataFrame, feature: str):
    chart = (
        alt.Chart(df)
        .mark_point()
        .encode(x=alt.X(feature).scale(zero=False), color=alt.Color("labels:N"))
    ).properties(width=500, height=250)
    return chart

    # just 1d for now..
    #
