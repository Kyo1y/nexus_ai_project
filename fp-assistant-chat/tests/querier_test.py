import pytest

from application.models import Query, QueryType
from application.querier import manager

@pytest.mark.parametrize(('model_output', 'expected_type'), (
    (None, QueryType.OOS),
    ('A', QueryType.PERFORMANCE),
    ('B', QueryType.NOT_WRITTEN),
    ('C', QueryType.AGENT_AMOUNT),
    ('d*', QueryType.OOS),
))
def test_converting(model_output: str, expected_type: QueryType):
    assert manager.convert_to_query_type(model_output) == expected_type