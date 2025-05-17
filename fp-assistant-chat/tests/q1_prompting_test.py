import pytest

from tests.conftest import get_data_from_file

from application.querier.prompts import get_performance_params

@pytest.mark.parametrize(('input_dict'), get_data_from_file('abnormal_volume_test_cases.csv'))
def test_selector(input_dict: dict):
    example = input_dict['example']
    business_volume = input_dict['business_volume']
    test_response = get_performance_params(example)
    assert business_volume == test_response, 'Abnormal Business Volume incorrect'