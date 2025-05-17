import pytest

from tests.conftest import get_data_from_file

from application.querier.prompts import get_user_intent

@pytest.mark.parametrize(('input_dict'), get_data_from_file('selector_test.csv'))
def test_selector(input_dict: dict):
    example = input_dict['example']
    question = input_dict['question']
    test_response = get_user_intent(example)
    assert test_response == question

