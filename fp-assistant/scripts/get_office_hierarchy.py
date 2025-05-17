"""
Run example: PYTHONPATH="${PYTHONPATH}:app/" python scripts/get_office_hierarchy.py
"""

import argparse
import json
import os
import re
import xml.etree.ElementTree as ET

import requests

parser = argparse.ArgumentParser(description='Used to get office hierarchy JSON')
parser.add_argument('-f', '--file', default='manager2office_codes.json', type=str)
parser.add_argument('-o', '--office', default='520', type=str, help='root office code to search under')
args = parser.parse_args()

json_path = args.file
root_office_code = args.office
if not re.search('\.json\s*$', json_path):
    print('Doesn\'t look like a file path, appending "manager2office_codes.json" to end of path')
    json_path = os.path.join(json_path, 'parent_office2child.json')

def get_office_children(office_code):
    AUTH_BASIC_TOKEN = 'UENTX1NWQzpQY3NQd2QxMjg='
    headers = {"Authorization": f"Basic {AUTH_BASIC_TOKEN}"}
    
    hiearchy_url = f'http://fcs.pennmutual.com/fcs-ws/hierarchy/{office_code}'
    response = requests.get(hiearchy_url, headers=headers)
    
    # Convert to element tree
    root = ET.fromstring(response.content)

    # Gather children
    children = [child.text for child in root.findall('Descendants/Descendant')]
    return children

parent_office2child = {}

# Get children
print('starting')
children = get_office_children(root_office_code)
# Save children
parent_office2child[root_office_code] = children

check_offices = {root_office_code: True, **{child: child in parent_office2child  for child in children}}
children_queue = {child for child, checked in check_offices.items() if not checked}
while children_queue:
    print('Check children:', end=' ')
    for child in children_queue:
        print(f'{child},', end=' ')
        office_children = get_office_children(child)
        parent_office2child[child] = office_children
        check_offices[child] = True
    print()
    children_queue = {child for child, checked in check_offices.items() if not checked}
    print('Children left in queue:', len(children_queue))
    with open(json_path, 'w') as j:
        json.dump(parent_office2child, j, indent=4)
