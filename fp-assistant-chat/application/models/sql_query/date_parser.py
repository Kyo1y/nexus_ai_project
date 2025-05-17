import datetime
import re
import logging

from calendar import monthrange
from dateutil.relativedelta import relativedelta
logger = logging.getLogger(__name__)

def convert_date_subtract(value1: str, value2: str) -> datetime.date:
    """Executes subtraction of two date values, checking for SQL specific syntax

    Args:
        value1 (str): first date
        value2 (str): second date

    Returns:
        datetime.date: evaluated date
    """
    if 'INTERVAL' in value2:
        if isinstance(value1, str):
            # Check for
            value1 = re.sub(r'[\'"](.*?)\1', r'\1', value1)
            date1 = datetime.datetime.strptime(value1, '%Y-%m-%d')
        else:
            date1 = value1
        # Need to convert
        new_value, dtype = re.search(r'INTERVAL\s+(\d+) (\S+)', value2).groups()
        # Instead of writing up logic for each of the interval type, pass in as kwarg to relative delta
        dtype = dtype.lower().strip()
        if not dtype.endswith('s'):
            dtype = dtype + 's'
        delta = relativedelta(**{dtype: int(new_value)})
        return date1 - delta

    else:
        date1 = datetime.datetime.strptime(value1, '%Y-%m-%d')
        date2 = datetime.datetime.strptime(value2, '%Y-%m-%d')
        return date1 - date2
    


def convert_date_subtract(base_date: str, interval_str: str) -> datetime:
    """Helper function to evaluate DATE_SUB with an interval."""
    match = re.match(r"INTERVAL (\d+) (\w+)", interval_str)
    if not match:
        raise ValueError("Invalid interval format")

    amount, unit = int(match.group(1)), match.group(2).upper()
    date_obj = datetime.datetime.strptime(base_date, '%Y-%m-%d')

    if unit == 'DAY' or unit == 'DAYS':
        return date_obj - datetime.timedelta(days=amount)
    elif unit == 'MONTH' or unit == 'MONTHS':
        return date_obj - datetime.timedelta(days=30*amount)  # Simplified month handling
    elif unit == 'YEAR' or unit == 'YEARS':
        return date_obj - datetime.timedelta(days=365*amount)  # Simplified year handling
    else:
        raise ValueError("Unsupported time unit")

def handle_date_subtract(input_str: str) -> str:
    """Parses SQL syntax for date subtraction and return the intended date."""
    date_sub_regex = r"DATE_SUB\('?(\d{4}-\d{2}-\d{2})'?,\s*(INTERVAL \d+ \w+)\)"
    
    while True:
        match = re.search(date_sub_regex, input_str)
        if not match:
            break  # No more DATE_SUB to process

        base_date, interval_str = match.groups()
        eval_date = convert_date_subtract(base_date, interval_str)
        input_str = input_str[:match.start()] + "'" + eval_date.strftime('%Y-%m-%d') + "'" + input_str[match.end():]

    return input_str

def update_curdate(input_string: str) -> str:
    """Replaces the SQL query function "CURRDATE()" with string of the current date.

    Args:
        input_string (str): SQL query

    Returns:
        str: _description_
    """
    return re.sub(r'CURDATE\(\)', str(datetime.date.today()), input_string)

def update_date_functions(input_str: str) -> str:
    # Hold information on columns to later update
    col2info = {}
    col2orig_str = {}
    # Assumption, only looking for MONTH and YEAR
    for match in re.finditer(r'(((YEAR|MONTH)\((.*?)\))\s*(\S*)\s*(\S*))', input_str, re.DOTALL):
        orig_str, func_call, func_name, col, opp, value = match.groups()
        col_dict = col2info.get(col, {})
        col_dict[func_name] = [opp, value]
        col2info[col] = col_dict
        col2orig_str[col] = orig_str
    
    # Process found information
    new_strs = {}
    for col_name, col_data in col2info.items():
        if 'MONTH' in col_data and 'YEAR' in col_data:
            month_op, month_val = col_data['MONTH']
            year_op, year_val = col_data['YEAR']
            if year_op == '=':
                if month_op == '=':
                    total_days = monthrange(int(year_val), int(month_val))[1]
                    new_strs[col_name] = f"{col_name} BETWEEN '{year_val}-{month_val:02d}-01' AND '{year_val}-{month_val:02d}-{total_days:02d}'"
                else:
                    new_strs[col_name] = f"{col_name} {month_op} '{year_val}-{month_val:02d}-01'"
            else:
                logger.warning(f'Unable to handle year op {year_op} and {month_op}')
        elif 'YEAR' in col_data:
            year_op, year_val = col_data['YEAR']
            if year_op == '=':
                new_strs[col_name] = f"{col_name} >= '{year_val}-01-01'"
            else:
                new_strs[col_name] = f"{col_name} {year_op} '{year_val}-01-01'"
        elif 'MONTH' in col_data:
            logger.warning(f'Odd case of finding MONTH function without YEAR, may need to check for errors.')

    for col, new_string in new_strs.items():
        old_str = col2orig_str[col]
        input_str = input_str.replace(old_str, new_string)
    
    return input_str

def replace(input_str: str) -> str:
    """Replaces SQL date related syntax with calculated values.

    Args:
        input_str (str): SQL query

    Returns:
        str: similar SQL query but with calculated values
    """

    ## TODO Need to remove DATE_SUB() and DATEDIFF()

    if 'CURDATE()' in input_str:
        input_str = update_curdate(input_str)
    if 'DATE_SUB' in input_str or 'INTERVAL' in input_str:
        input_str = handle_date_subtract(input_str)
    if 'YEAR' in input_str or 'MONTH' in input_str:
        try:
            input_str = update_date_functions(input_str)
        except:
            logger.exception(f'Unable to remove date functions.')
    return input_str


if __name__ == '__main__':
    # sql_string = """
    #     SELECT agent, name, MAX(isdt)
    #     FROM policy_data
    #     WHERE prim_ofcd = 'B56' AND agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE isdt > DATE_SUB('2024-05-24', INTERVAL 8 MONTH)
    #     )
    #     GROUP BY agent, name
    # """

    sql_string = """
        SELECT agent, name, MIN(famt) as min_famt, COUNT(pid) as policy_count
        FROM policy_data
        WHERE agent NOT IN (
            SELECT agent
            FROM policy_data
            WHERE famt < 50000 AND isdt >= DATE_SUB('2024-05-24', INTERVAL 3 MONTH)
        )
        GROUP BY agent, name
    """

    # sql_string = """
    #     SELECT agent, name, MIN(famt) as min_famt, COUNT(pid) as policy_count
    #     FROM policy_data
    #     WHERE agent NOT IN (
    #         SELECT agent
    #         FROM policy_data
    #         WHERE famt < 75000 AND isdt >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    #     )
    #     GROUP BY agent, name
    # """

    clean_sql_stirng = replace(sql_string)
    print(clean_sql_stirng)