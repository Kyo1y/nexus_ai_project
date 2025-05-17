import pytest

from tests.conftest import get_data_from_file

from application.querier.prompts import get_not_written_params
from application.querier.prompts.extract import date_value

@pytest.fixture(scope='class', params=get_data_from_file('written_policies_test_cases.csv'))
def q2_fixtures(request):
    input_dict = request.param
    example = input_dict['example']
    written_policy = input_dict['written']
    date_range = input_dict['date_range']

    # Need to parse the date value here
    date_val = input_dict['date_value']
    date_val_extracted = date_value(date_val, date_range)

    request.cls.expected_written_policy = written_policy
    request.cls.expected_date_range = date_range
    request.cls.expected_date_value = date_val_extracted

    is_q2, test_date_range, test_date_value, test_written_policy = get_not_written_params(example)
    request.cls.extracted_written_policy = test_written_policy
    request.cls.extracted_date_range = test_date_range.lower()
    request.cls.extracted_date_value = test_date_value

@pytest.mark.usefixtures('q2_fixtures')
class TestQ2: 
    def test_written_policy(self):
        assert self.expected_written_policy == self.extracted_written_policy, 'Q2 Written check failed'
    
    def test_date_range(self):
        assert self.expected_date_range == self.extracted_date_range, 'Q2 Date Range check failed'
    
    def test_date_value(self):
        assert self.expected_date_value == self.extracted_date_value, 'Q2 Date Value check failed'

