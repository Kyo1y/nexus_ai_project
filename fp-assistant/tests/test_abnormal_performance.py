from app.routers.data_analysis_router import AgentAnalysisRequestData
from app.services.data_analysis.agent_data import get_agent_analysis

import pandas as pd
import pytest

@pytest.fixture
def result_df():
    input_data = AgentAnalysisRequestData(
        name='agent_analysis',
        period={
            "unit" : 'months',
            "value": 12,
            "frequency": 'M'
        }
    )
    result = get_agent_analysis(input_data)
    df = pd.DataFrame(result)
    return df

def test_labels(result_df):
    labels = result_df['label']
    label_values = {'high', 'low'}
    assert all([label in label_values for label in labels])

def test_null_values(result_df):
    assert not result_df.isnull().values.any()

def test_z_scores(result_df):
    z_scores = result_df['z_score']
    assert all([(z_score < -1 or z_score > 1) for z_score in z_scores])


if __name__ == "__main__":
    pytest.main()