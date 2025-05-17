import pytest

from tests.conftest import get_data_from_file

from application.querier.prompts import get_agent_amount_params
from application.querier.prompts.extract import extract_date_q3, amount_value


@pytest.fixture(scope='class', params=get_data_from_file('face_amount_test_cases.csv'))
def q3_fixtures(request):
    input_dict = request.param
    example = input_dict['example']
    written_policy = input_dict['written']
    date_range = input_dict['date_range']
    amount_range = input_dict['amount_range']

    amount_val = input_dict['amount_value']
    amount_val_extracted = amount_value(amount_val, amount_range)

    # Need to parse the date value here
    date_val = input_dict['date_value']
    # date_val_extracted = date_value(date_val, date_range)
    date_range_extracted, date_val_extracted = extract_date_q3(date_val)

    request.cls.expected_written_policy = written_policy
    # request.cls.expected_date_range = date_range
    request.cls.expected_date_value = date_val_extracted
    request.cls.expected_amount_range = amount_range
    request.cls.expected_amount_value = amount_val_extracted

    is_face_amount, test_date_range, test_date_value, test_face_amount_range, test_face_amount_value, test_written_policy = get_agent_amount_params(example)
    request.cls.extracted_written_policy = test_written_policy
    # request.cls.extracted_date_range = test_date_range.lower()
    request.cls.extracted_date_value = test_date_value
    request.cls.extracted_amount_range = test_face_amount_range.lower()
    request.cls.extracted_amount_value = test_face_amount_value

@pytest.mark.usefixtures('q3_fixtures')
class TestQ3:
    def test_written_policy(self):
        assert self.expected_written_policy == self.extracted_written_policy, 'Q3 Written check failed'
    
    # def test_date_range(self):
    #     assert self.expected_date_range == self.extracted_date_range, 'Q3 Date Range check failed'
    
    def test_amount_range(self):
        assert self.expected_amount_range == self.extracted_amount_range, 'Q3 Amount Range check failed'
    
    def test_date_value(self):
        assert self.expected_date_value == self.extracted_date_value, 'Q3 Date Value check failed'
    
    def test_amount_value(self):
        assert self.expected_amount_value == self.extracted_amount_value, 'Q3 Amount Value check failed'

