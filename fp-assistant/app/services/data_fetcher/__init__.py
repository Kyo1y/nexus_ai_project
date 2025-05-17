from config import get_settings
from services.data_fetcher.connector import DataManagerConnector

manager_url = get_settings().DATA_URL
data_connector = DataManagerConnector(manager_url)