import pandas as pd
from datetime import datetime
import pytest
from app.services.data_analysis.transformers import FieldFilter


@pytest.fixture
def test_data():
    return pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'policies': [50, 100, 150],
        'category': ['app', 'inforce', 'pending']
    })

def test_date_greater_than(test_data):
    filter_obj = FieldFilter('date', '>', datetime.strptime('2023-01-01', '%Y-%m-%d').date())
    filtered_data = filter_obj(test_data)
    assert len(filtered_data) == 2

def test_policies_less_than_equal(test_data):
    filter_obj = FieldFilter('policies', '<=', 100)
    filtered_data = filter_obj(test_data)
    assert len(filtered_data) == 2

def test_category_equal(test_data):
    filter_obj = FieldFilter('category', '==', 'inforce')
    filtered_data = filter_obj(test_data)
    assert len(filtered_data) == 1
    assert filtered_data['category'].iloc[0] == 'inforce'

def test_category_in(test_data):
    filter_obj = FieldFilter('category', 'in', ['app', 'inforce'])
    filtered_data = filter_obj(test_data)
    assert len(filtered_data) == 2
    assert filtered_data['category'].isin(['app', 'inforce']).all()


def test_invalid_operator(test_data):
    with pytest.raises(ValueError):
        FieldFilter('category', 'invalid', 'inforce')(test_data)

def test_invalid_field(test_data):
    with pytest.raises(KeyError):
        FieldFilter('non_existent_field', '==', 'value')(test_data)
