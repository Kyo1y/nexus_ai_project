from application.models import SQLQuery
from application.requestor.connectors import APIConnector

if __name__ == '__main__':

    base_url = 'http://127.0.01:5001/api/v1'
    connector = APIConnector(base_url=base_url)
    
    query_text = """
        FROM policy_data
        WHERE agent NOT IN (
            SELECT agent
            FROM policy_data
            WHERE isdt >= '2023-01-01'
        )
        GROUP BY agent, name
    """
    query = SQLQuery(query_text)

    response = connector.process(query)
    print(response)