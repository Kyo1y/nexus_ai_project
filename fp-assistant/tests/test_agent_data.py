import numpy as np
import pandas as pd
from app.services.data_analysis.agent_data import calculate_z_score_for_row, calculate_z_score, calculate_abnormality

def test_calculate_z_score():
    # Test with normal data
    performances = np.array([2, 4, 6, 8, 10])
    z_scores = calculate_z_score(performances)
    expected_z_scores = np.array([-1.41421356, -0.70710678, 0., 0.70710678, 1.41421356])
    assert np.allclose(z_scores, expected_z_scores, rtol=1e-5)

    # Test with NaN values
    performances_with_nan = np.array([2, 4, np.nan, 8, 10])
    z_scores_with_nan = calculate_z_score(performances_with_nan)
    expected_z_scores_with_nan = np.array([-1.26491106, -0.63245553, 0.63245553, 1.26491106])
    assert np.allclose(z_scores_with_nan, expected_z_scores_with_nan, rtol=1e-5)

    # Test with all NaN values
    all_nan_performances = np.array([np.nan, np.nan, np.nan])
    z_scores_all_nan = calculate_z_score(all_nan_performances)
    assert np.all(np.isnan(z_scores_all_nan))


def test_calculate_z_score_for_row():
    # Test with normal data
    row = pd.Series({'AgentCode': '123', 'name': 'John', 'Jan': 2, 'Feb': 4, 'Mar': 6, 'Apr': 8, 'May': 10})
    z_score = calculate_z_score_for_row(row)
    expected_z_score = 1.41421356
    assert np.allclose(z_score, expected_z_score, rtol=1e-5)

    # Test with NaN values
    row_with_nan = pd.Series({'AgentCode': '123', 'name': 'John', 'Jan': 2, 'Feb': '4', 'Mar': np.nan, 'Apr': 8, 'May': 10})
    z_score_with_nan = calculate_z_score_for_row(row_with_nan)
    expected_z_score_with_nan = 1.26491106
    assert np.allclose(z_score_with_nan, expected_z_score_with_nan, rtol=1e-5)


def test_calculate_abnormality():
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

test_calculate_z_score()
test_calculate_z_score_for_row()
test_calculate_abnormality()
