import os

import pandas as pd
import pytest

data_dir = os.path.join(os.path.dirname(__file__), 'data/')

def get_rows(data_frame):
    test_inputs = []
    for i, row in data_frame.iterrows():
        test_inputs.append(dict(row.where(pd.notna(row), None)))
    return test_inputs


def get_data_from_file(file_name):
    df = pd.read_csv(os.path.join(data_dir, file_name))
    return get_rows(df)

if __name__ == '__main__':
    
    dpath = 'selector_test.csv'
    data = get_data_from_file(dpath)
    print(data)