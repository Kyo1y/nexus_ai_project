import logging

logger = logging.getLogger("logger")

filter_key_list = ['famt']
time_unit_key_list = ['days', 'months', 'years']

def build_filter_query(query_data):
    for query_filter in  query_data.filter:
        if query_filter['key'] not in filter_key_list:
            raise Exception("unknown filter key")
        else:
            query_str = query_filter['key'] + convert_to_symbol(query_filter['operator']) + str(query_filter['value'])
            return query_str

def convert_to_symbol(operator_str):
    if operator_str == 'greater':
        return ' > '
    elif operator_str == 'less':
        return ' < '
    elif operator_str == 'equal':
        return ' == '
    else:
        raise Exception("unknown operator")
