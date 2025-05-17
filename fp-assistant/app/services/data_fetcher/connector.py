import json
import os
import logging

import requests
logger = logging.getLogger("logger")
class DataManagerConnector:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_data(self) -> str:
        endpoint = 'agentdata'
        
        response = requests.post(os.path.join(self.base_url, endpoint),
                                 data=json.dumps({'output_format': 'csv'}),
                                 headers={
                                     'Content-Type': 'application/json'
                                     }
                                )
        logger.info(f'request made to {os.path.join(self.base_url, endpoint)}')
        return response.content.decode('utf-8')