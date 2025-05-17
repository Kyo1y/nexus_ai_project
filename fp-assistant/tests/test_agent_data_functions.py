import numpy as np
import pandas as pd
import pytest


def calculate_z_score(performances: np.ndarray) -> np.ndarray:
    """
    Calculate the Z-scores for a given array of past performances.

    Parameters:
    performances (np.ndarray): Array of past performances (may contain NaN).

    Returns:
    np.ndarray: Array of Z-scores corresponding to the input performances.
    """
    # Convert performances to numeric type and handle non-numeric values
    performances = performances[~np.isnan(performances)]
    performances = pd.to_numeric(performances, errors='coerce')

    # Calculate mean and standard deviation
    mean = np.mean(performances)
    std_dev = np.std(performances)

    # Calculate Z-score for each performance
    z_scores = (performances - mean) / std_dev

    return z_scores


def calculate_z_score_for_row(row: pd.Series) -> float:
    """
    Calculate the mean z-score for a given row of data.

    Parameters:
    row (pd.Series): A pandas Series representing a single row of data.

    Returns:
    float: The mean z-score calculated for the row.
    """
    # Exclude 'agent_code' and 'name' columns and convert the rest to numeric
    row_values = pd.to_numeric(row.drop(['AgentCode', 'name']), errors='coerce').values

    # Calculate z-scores for the row values
    z_scores = calculate_z_score(row_values)

    # Take just the last completed month
    z_score = z_scores[-1]

    return z_score


def calculate_abnormality(ratio, upper_threshold=1.5, lower_threshold=0.5) -> str:
    """
    Determine abnormality based on the given ratio and threshold.

    Parameters:
    ratio (float): Ratio of the current volume to historical average.
    threshold (float): Threshold value for abnormality (default is 1.5).

    Returns:
    str: Abnormality label ('high' or 'low').
    """
    if ratio > upper_threshold:
        return 'high'
    elif ratio < lower_threshold:
        return 'low'
    else:
        return ''


def test_calculate_z_score():
    # Test with normal data
    performances = np.array([2, 4, 6, 8, 10])
    z_scores = calculate_z_score(performances)
    expected_z_scores = np.array([-1.41421356, -0.70710678, 0., 0.70710678, 1.41421356])
    assert np.allclose(z_scores, expected_z_scores, rtol=1e-5)

    # Test with NaN values
    performances_with_nan = np.array([2, 4, np.nan, 8, 10])
    z_scores_with_nan = calculate_z_score(performances_with_nan)
    expected_z_scores_with_nan = np.array([-1.34164079, -0.67082039, np.nan, 0.67082039, 1.34164079])
    expected_z_scores_with_nan = np.array([-1.26491106, -0.63245553, 0.63245553, 1.26491106])
    assert np.allclose(z_scores_with_nan, expected_z_scores_with_nan, rtol=1e-5)


def test_calculate_z_score_for_row():
    """
    Verify whether calculate_z_score_for_row function works as expected
    """
    # Test with normal data
    row = pd.Series({'AgentCode': '123', 'name': 'John', 'Jan': 2, 'Feb': 4, 'Mar': 6, 'Apr': 8, 'May': 10})
    z_score = calculate_z_score_for_row(row)
    expected_z_score = 1.41421356  # Calculated manually based on the provided test data
    assert np.allclose(z_score, expected_z_score, rtol=1e-5)

    # Test with NaN values
    row_with_nan = pd.Series({'AgentCode': '123', 'name': 'John', 'Jan': 2, 'Feb': '4', 'Mar': np.nan, 'Apr': 8, 'May': 10})
    z_score_with_nan = calculate_z_score_for_row(row_with_nan)
    expected_z_score_with_nan = 1.26491106  # Calculated manually based on the provided test data
    assert np.allclose(z_score_with_nan, expected_z_score_with_nan, rtol=1e-5)


def test_calculate_abnormality():
    """
    Verify whether calculate_abnormality function works as expected
    """
    # Test with high ratio
    high_ratio = 3.0
    assert calculate_abnormality(high_ratio) == 'high'

    # Test with low ratio
    low_ratio = 0.2
    assert calculate_abnormality(low_ratio) == 'low'

    # Test with ratio between upper and lower threshold
    normal_ratio = 1.0
    assert calculate_abnormality(normal_ratio) == ''

    # Test with custom thresholds
    custom_upper_threshold = 2.5
    custom_lower_threshold = 0.3
    assert calculate_abnormality(high_ratio, custom_upper_threshold, custom_lower_threshold) == 'high'
    assert calculate_abnormality(low_ratio, custom_upper_threshold, custom_lower_threshold) == 'low'
    assert calculate_abnormality(normal_ratio, custom_upper_threshold, custom_lower_threshold) == ''


if __name__ == "__main__":
    pytest.main()