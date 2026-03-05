from sklearn.neighbors import NearestNeighbors
import numpy as np


def fit_neighbors(samples: np.ndarray, n: int):
    model = NearestNeighbors(n_neighbors=n)
    model.fit(samples)
    return model


def show_neighbors_one(model: NearestNeighbors, sample: np.ndarray):
    return model.kneighbors(sample)


def show_groups():
    pass
