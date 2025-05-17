import numpy as np

def convert_to_z_scores(arr: np.ndarray):
    mean = arr.mean()
    return