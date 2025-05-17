import json
import os

# Paths of the files
file_paths = [
    'app/data_manager/agents/parent_office2child.json',
    'app/data_manager/agents/manager2office_codes.json'
]

# Check each file in the list
for file_path in file_paths:
    # Check if the file exists
    if not os.path.exists(file_path):
        # Create the directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Create an empty JSON file
        with open(file_path, 'w') as f:
            json.dump({}, f)
        print(f"Created empty file: {file_path}")
    else:
        print(f"File exists: {file_path}")

# Load the JSON files
try:
    with open('app/data_manager/agents/parent_office2child.json', 'r') as f:
        parent_office2child = json.load(f)
except FileNotFoundError:
    print("The file parent_office2child.json was not found.")
    parent_office2child = {}

try:
    with open('app/data_manager/agents/manager2office_codes.json', 'r') as f:
        manager2office_codes = json.load(f)
except FileNotFoundError:
    print("The file manager2office_codes.json was not found.")
    manager2office_codes = {}

# Your code continues from here...
