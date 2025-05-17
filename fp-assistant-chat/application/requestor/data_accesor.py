
from application.configs import config
from application.models import Query, QueryType
from application.models import Response
from application.requestor.connectors import Connector, JSONMockConnector, JSONMockConnectorV2, XLSXMockConnector, CSVMockConnector, APIConnector

def get_data(query: Query) -> Response:
    connector = get_connector()
    if isinstance(query, (Query.oos, Query.explain)):
        response = Response(query=query)
    else:
        response = connector.process(query)
    return response


def get_connector() -> Connector:
    """Get connector to access data

    Raises:
        ValueError: config value set to improper value

    Returns:
        Connector: connector to access data
    """
    # TODO: Update with real connector when available
    if config.CONNECTOR_VERSION == 'APIConnector':
        connector = APIConnector('http://127.0.01:5001/api/v1')
    elif config.CONNECTOR_VERSION == 'JSONMockConnector':
        connector = JSONMockConnector()
    elif config.CONNECTOR_VERSION == 'JSONMockConnectorV2':
        connector = JSONMockConnectorV2()
    elif config.CONNECTOR_VERSION == 'XLSXMockConnector':
        connector = XLSXMockConnector()
    elif config.CONNECTOR_VERSION == 'CSVMockConnector':
        connector = CSVMockConnector()
    else:
        raise ValueError(f'Connector config must be recognized value, not "{config.CONNECTOR_VERSION}". See data_accesor.py for available versions.')
    return connector
