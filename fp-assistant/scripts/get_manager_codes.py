"""
Run example: PYTHONPATH="${PYTHONPATH}:app/" python scripts/get_manager_codes.py
"""

import argparse
import json
import os
import re

import pandas as pd
import requests

from app.data_manager import datamanager

parser = argparse.ArgumentParser(description='Used to get manager codes JSON')
parser.add_argument('-f', '--file', default='manager2office_codes.json', type=str)

args = parser.parse_args()

file_name = args.file
if not re.search('\.json\s*$', file_name):
    print('Doesn\'t look like a file path, appending "manager2office_codes.json" to end of path')
    file_name = os.path.join(file_name, 'manager2office_codes.json')


pcs_query = datamanager.Query(base_url='http://fcs.pennmutual.com/fcs-ws/system/search',
                            q=f'active:true AND ptyp:Person AND flofcd:520 AND roles:"FIELD MGMT"',
                            # fq=fq,
                            # fl='agcds,pid,source,isdt,mddt,edt,edtmn,edtyr,famt,puwamt,pamt,apamt,mdpremamt,totannpremamt',
                            wt='json', rows=500, decrypt=True, start=0)
# Get data
response = requests.get(pcs_query.url(), headers={'Authorization': 'Basic UENTX1NWQzpQY3NQd2QxMjg='})

# Manage data using pandas DF
data = json.loads(response.content)
agents_df = pd.DataFrame(data['response']['docs'])

manager2office_codes = pd.Series(agents_df['ofcds'].values, index=agents_df['nm']).to_dict()
with open(file_name, 'w') as f:
    json.dump(manager2office_codes, f, indent=4)