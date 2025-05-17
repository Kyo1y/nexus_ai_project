import datetime
from dateutil.relativedelta import relativedelta

import pytest

from application.models import Period, Query, QueryType
from application.requestor import connectors

@pytest.fixture
def period():
    period = Period(start=datetime.datetime(2023, 1, 1), 
                        end=datetime.datetime(2024, 1, 1), 
                        interval=relativedelta(months=12))
    return period

class TestXLSXMock:
    @pytest.fixture(scope='class')
    def connector(self):
        connector = connectors.XLSXMockConnector()
        return connector

    def test_process_entry_low(self, connector: connectors.XLSXMockConnector, period: Period):
        query = Query(QueryType.LOW, period=period)
        response = connector.process(query)
        assert response

    def test_process_entry_high(self, connector: connectors.XLSXMockConnector, period: Period):
        query = Query(QueryType.HIGH, period=period)
        response = connector.process(query)
        assert response

    def test_process_entry_both(self, connector: connectors.XLSXMockConnector, period: Period):
        query = Query(QueryType.BOTH, period=period)
        response = connector.process(query)
        assert response

    def test_process_entry_failure(self, connector: connectors.XLSXMockConnector):
        query = Query(QueryType.OOS, period=period)
        with pytest.raises(ValueError, match=r'need to configure in Connector'):
            response = connector.process(query)
        assert True
