from app.data_manager import datamanager, lookups
from app.services.data_analysis import transformers
from app.data_manager import datamanager, lookups
from app.services.data_analysis import transformers

from app.services.query_builder import build_filter_query
from app.utils.date_util import get_current_date, get_previous_date

import datetime
from dateutil.relativedelta import relativedelta
date_format = '%Y-%m-%dT%H:%M:%SZ'
import json
import logging
import pandas as pd
import re

import numpy as np
import scipy.stats as stats
import statistics

logger = logging.getLogger("logger")

async def get_agent_count(request_data):
    df = datamanager.collect()
    # df = pd.read_csv(io.StringIO(string_data))
    logger.info('Starting')
    if request_data.name == "over_amount":
        df = df.loc[(df['isdt'] > get_previous_date(request_data.period['unit'], request_data.period['value'])) & (df['isdt'] < get_current_date())]
        df = df.groupby(['AgentCode', 'name'], as_index=False)['famt'].max()
        df = df.query(build_filter_query(request_data))
    elif request_data.name == "not_written":
        df = df.loc[df['source'] == 'inforce']
        df = df.sort_values(by="isdt").drop_duplicates(['AgentCode', 'name'], keep="last")
        df = df[['AgentCode','name','isdt']]  
        df = df.loc[(df['isdt'] < get_previous_date(request_data.period['unit'], request_data.period['value']))]
    else:
        raise Exception("unknown name key")

    return {
        "count" : len(df),
        "agent_list": json.loads(df.to_json(orient='records'))
    }

async def data_querying(request_json):
    # Create transformation objects
    logger.debug('Creating transformation objects from request data...')

    filters = transformers.create_filters(request_json.filters)
    grouping = transformers.Grouping(**request_json.grouping)
    group_filters = transformers.create_filters(request_json.group_filters)

    # TODO: refactor so more logical
    if request_json.identity:
        name = request_json.identity
        # Convert name to agent code
        office_codes = lookups.manager2office_codes.get(name, None)
        if office_codes:
            # From agent code, filter available offices
            identity_filter_dict = {'field': 'prim_ofcd', 'items': office_codes}
            filters = transformers.create_filters([identity_filter_dict]) + filters
        else:
            logger.warning(f'Identity "{name}" passed but did not match records')
        

    # Debug:
    logger.debug(f'Filters: {filters}, Grouping: {grouping}, Group Filters: {group_filters}')


    # Request data
    df = datamanager.collect()

    # Create baseline filters:
    if all(['source' != filter_obj.field for filter_obj in filters]):
        filters.insert(0, transformers.Value(field='source', items=['inforce']))

    sub_df = df.copy()

    for filterer in filters:
        sub_df = filterer(sub_df)

    grouped_data = grouping(sub_df)

    # Filters data
    results = grouped_data.copy()
    for filterer in group_filters:
        results = filterer(results)


    results['agent'] = results['AgentCode']
    del results['AgentCode']

    # Final formatting
    float_cols = results.select_dtypes(include=['float']).columns
    results[float_cols] = results[float_cols].round(2)

    results = results.dropna()

    return {
        "count" : len(results),
        "agent_list": json.loads(results.to_json(orient='records')),
        "dtypes": results.dtypes.astype(str).to_dict()
        }

def resample_policy_data_with_name(df, interval_start, interval_end, date_col='isdt', agent_col='agent', name_col='name', start_date_col='strdt'):
    """
    Resamples policy data by the specified frequency (monthly or quarterly) for each agent,
    keeping the agent's name and an existing start date (strdt) for each agent in the final DataFrame,
    without modifying the original DataFrame.

    Parameters:
    - df: DataFrame containing the policy data.
    - date_col: The name of the column containing the policy issue dates.
    - agent_col: The name of the column containing the agent identifiers.
    - name_col: The name of the column containing the agent names.
    - start_date_col: The name of the column containing the start date for each agent.
    - resample_freq: The frequency for resampling ('M' for monthly, 'Q' for quarterly).

    Returns:
    - A pivot table DataFrame where each row corresponds to an agent (with name and start date),
      each column to the specified time period, and cell values represent the count of policies issued during that period.
    """

    df_copy = df.copy()

    # Ensure the date column is in datetime format
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])

    df_copy.set_index(date_col, inplace=True)

    # Preserve the first occurrence of the agent's name and start date within the group
    df_copy[name_col] = df_copy.groupby(agent_col)[name_col].transform('first')
    df_copy[start_date_col] = df_copy.groupby(agent_col)[start_date_col].transform('first')

    # Get the first day of the month for interval_start
    start_date = interval_start - pd.offsets.MonthBegin(1)
    date_range = pd.date_range(start=start_date, end=interval_end, freq='3M')

    df_copy['bin'] = pd.cut(df_copy.index, bins=date_range)
    df_copy = df_copy.reset_index()

    # Group by agent_col, name_col, and 'bin', then count the occurrences
    resampled_counts = df_copy.groupby([agent_col, 'bin']).size().reset_index(name='PolicyCount')    

    # Create pivot table
    pivot_table = resampled_counts.pivot_table(index=[agent_col], columns='bin', values='PolicyCount', aggfunc='sum').fillna(0)
    pivot_table.columns = [col.right.strftime('%Y-%m') if isinstance(col.right, pd.Timestamp) else col for col in pivot_table.columns]
    pivot_table.reset_index(inplace=True)

    pivot_table = pd.merge(df_copy[[agent_col, name_col, start_date_col]], pivot_table, on=agent_col, how='right').drop_duplicates()

    return pivot_table

def get_policy_columns(df):
    """
    Identifies and returns a list of column names that are in the "YYYY-mm" format, 
    which are assumed to represent policy columns.

    Parameters:
    - df: DataFrame containing the dataset with potentially date-formatted column names.

    Returns:
    - A list of column names that match the "YYYY-mm" format.
    """
    # Regular expression pattern to match columns in the "YYYY-mm" format
    date_pattern = re.compile(r'^\d{4}-\d{2}$')
    
    # Filter and return column names that match the pattern
    policy_columns = [col for col in df.columns if date_pattern.match(col)]
    
    return policy_columns

def find_last_full_month_column(policy_columns):
    """
    Identifies the last full month column before the current date.
    
    Parameters:
    - policy_columns: A list of column names in the "YYYY-mm" format.
    
    Returns:
    - The column name representing the last full month.
    """
    current_date = datetime.datetime.now()
    last_month_date = current_date.replace(day=1) - datetime.timedelta(days=1)  # This ensures we get the last full month
    
    # Convert column names to datetime and filter out any that are in the future
    policy_dates = [datetime.datetime.strptime(col, '%Y-%m') for col in policy_columns]
    policy_dates = [date for date in policy_dates if date <= last_month_date]
    
    if policy_dates:
        # Find the most recent policy column
        most_recent_policy_date = max(policy_dates)
        most_recent_policy_column = most_recent_policy_date.strftime('%Y-%m')
        return most_recent_policy_column
    else:
        return None

def calculate_three_month_average_growth(df):
    """
    Calculates the three-month average growth rate for policy columns.
    """
    policy_columns = get_policy_columns(df)
    if len(policy_columns) < 4:
        # Not enough data to calculate three-month growth
        return np.nan
    
    # Calculate month-over-month growth rates
    growth_rates = df[policy_columns].pct_change(axis=1)
    
    # Calculate the average growth rate of the latest three months
    three_month_avg_growth = growth_rates.iloc[:, -3:].mean(axis=1)
    
    return three_month_avg_growth

def get_last_completed_period(current_date, period_type):
    """
    Calculates the date of the last completed month or quarter.

    Parameters:
    - current_date: The current date as a datetime object.
    - period_type: 'M' for month or 'Q' for quarter.

    Returns:
    - The date (as a string in 'YYYY-MM-DD' format) of the last day of the last completed month or quarter.
    """
    if period_type == 'M':
        # Subtract a day from the first day of the current month to get the last day of the last month
        last_day_of_last_month = current_date.replace(day=1) - relativedelta(days=1)
        return last_day_of_last_month
    elif period_type == 'Q':
        # Calculate the start of the current quarter, then subtract a day to get the end of the last quarter
        current_quarter_start_month = 3 * ((current_date.month - 1) // 3) + 1
        start_of_current_quarter = current_date.replace(month=current_quarter_start_month, day=1)
        last_day_of_last_quarter = start_of_current_quarter - relativedelta(days=1)
        return last_day_of_last_quarter
    else:
        raise ValueError("Invalid period type. Use 'M' for month or 'Q' for quarter.")

def create_df_by_frequency(df, request_data, frequency, policy_type=['inforce']):

    df['isdt'] = pd.to_datetime(df['isdt'], errors='coerce').dt.date
    df['strdt'] = pd.to_datetime(df['strdt'], errors='coerce').dt.date

    last_completed_frequency_period = get_last_completed_period(datetime.datetime.now(), frequency).date()
    df = df.loc[(df['isdt'] > get_previous_date(request_data.period['unit'], request_data.period['value'])) & (df['isdt'] < last_completed_frequency_period) & (df['strdt'] < get_previous_date(request_data.period['unit'], request_data.period['value']))]
    df = df.loc[df['source'].isin(policy_type)]
    df = df.sort_values(by=["name","agent", "strdt"])
    df = resample_policy_data_with_name(df, interval_start=get_previous_date(request_data.period['unit'], request_data.period['value']), interval_end=last_completed_frequency_period)

    logger.debug("Detailed with Policies per Frequency\n" + str(df))
    df['z_score'] = df.apply(lambda row: calculate_z_score_for_row(row), axis=1)

    return df

def analyze_df(df):

    policy_columns = get_policy_columns(df)
    df['total_number_of_policies'] = df[policy_columns].sum(axis=1)

    # Calculate historical average
    df['historical_average'] = df['total_number_of_policies'] / (len(policy_columns))
    df['policy_median'] = df[policy_columns].median(axis=1)

    current_volume_col = find_last_full_month_column(policy_columns)
    df['current_volume'] = df[current_volume_col]
    df['avg_ratio'] = df['current_volume'] / df['historical_average'].replace(0, np.nan)  # Avoid division by zero
    df['median_ratio'] = df['current_volume'] / df['policy_median'].replace(0, np.nan)
    df['three_month_average_growth_rate'] = calculate_three_month_average_growth(df)

    return df

def combine_analyses(monthly_result, quarterly_result):
    combined_df = pd.merge(quarterly_result, monthly_result, how='left', on=['agent', 'name'], suffixes=('_quarterly', '_monthly'))
    return combined_df

async def get_agent_analysis(request_data):

    df = datamanager.collect()
    policy_type = ['inforce']

    df = create_df_by_frequency(df, request_data, 'Q', policy_type=policy_type)

    if len(df.columns) < 4:
        return {"error": "insufficient data points available for the current date range"}

    df = analyze_df(df)

    # Filter out "low" values under threshold for "average"
    policy_median_cutoff = 2.5
    upper_z_score_threshold = 1
    lower_z_score_threshold = -1

    df = df.loc[(df['policy_median'] >= policy_median_cutoff)]
    df['abnormality_value'] = df.apply(lambda row: calculate_abnormality(row['z_score'], upper_z_score_threshold, lower_z_score_threshold), axis=1)
    df = df[df['abnormality_value'] != '']
 
    # Reformat data frame
    # df['agent'] = df['AgentCode']
    df['label'] = df['abnormality_value']
    # del df['AgentCode']
    del df['abnormality_value']
    df = df[['agent', 'name', 'historical_average', 'current_volume', 'policy_median', 'z_score', 'label']]

    # Update data so it is not too long
    float_cols = df.select_dtypes(include=['float']).columns
    df[float_cols] = df[float_cols].round(2)

    json_results = json.loads(df.to_json(orient='records'))
    #########

    return json_results

def insert_agent_information(df, agent_data_list):
    for agent_data in agent_data_list:
        row = df.loc[df['agent_id'] == agent_data['agent_id']]
        agent_data['name'] = str(row['name'].values[0])
        agent_data['agent_code'] = str(row['agent_code'].values[0])
        del agent_data['agent_id']

def remove_outliers(df, q_test_threshold):
    data = df['total_number_of_policies'].to_list()
    mean = statistics.mean(data)
    statistic, p_value = stats.mstats.normaltest(data)
    contributions = (data - np.float64(mean))**2 / np.var(data)
    # outliers = [data[i] for i in range(len(data)) if contributions[i] > q_test_threshold]
    tmp_df = df.assign(contributions = contributions)
    return tmp_df.query('(contributions < ' + str(q_test_threshold) + ' & total_number_of_policies < ' + str(mean) + ') or (total_number_of_policies > ' + str(mean) + ')')


def calculate_z_score(performances: np.ndarray) -> np.ndarray:
    """
    Calculate the Z-scores for a given array of past performances.

    Parameters:
    performances (np.ndarray): Array of past performances (may contain NaN).

    Returns:
    np.ndarray: Array of Z-scores corresponding to the input performances.
    """
    # Convert performances to numeric type and handle non-numeric values
    performances = performances[~np.isnan(performances)]
    performances = pd.to_numeric(performances, errors='coerce')

    # Calculate mean and standard deviation
    mean = np.mean(performances)
    std_dev = np.std(performances)

    # Calculate Z-score for each performance
    z_scores = (performances - mean) / std_dev

    return z_scores

def calculate_z_score_for_row(row: pd.Series) -> float:
    """
    Calculate the mean z-score for a given row of data.

    Parameters:
    row (pd.Series): A pandas Series representing a single row of data.

    Returns:
    float: The mean z-score calculated for the row.
    """
    # Exclude 'agent_code' and 'name' columns and convert the rest to numeric
    row_values = pd.to_numeric(row.drop(['agent', 'name']), errors='coerce').values

    # Calculate z-scores for the row values
    z_scores = calculate_z_score(row_values)

    # Take just the last completed month
    z_score = z_scores[-1]

    return z_score

def calculate_threshold(historical_average, percentage=10):
    """
    Calculate the threshold based on the historical average and a percentage.

    Parameters:
    total_number_of_policies (float): Total number of policies.
    historical_average (float): Historical average.
    percentage (float): Percentage above or below the historical average for the threshold (default is 10%).

    Returns:
    float: Calculated threshold value.
    """
    historical_average = historical_average.mean()
    threshold = historical_average * (1 + percentage / 100)
    return threshold

def calculate_abnormality(value, upper_threshold=1, lower_threshold=-1) -> str:
    """
    Determine abnormality based on the given ratio and threshold.

    Parameters:
    ratio (float): Ratio of the current volume to historical average.
    threshold (float): Threshold value for abnormality (default is 1.5).

    Returns:
    str: Abnormality label ('high' or 'low').
    """
    if value > upper_threshold:
        return 'high'
    elif value < lower_threshold:
        return 'low'
    else:
        return ''  


def chunk_data(policy_data: pd.DataFrame, frequency: str) -> pd.Series:
    """
    Count the number of policies in the given frequency across a set timespan.

    Parameters:
    policy_data (pd.DataFrame): Policy level data with a 'date' column.
    frequency (str): Frequency for chunking the data ('monthly', 'quarterly', 'yearly').

    Returns:
    pd.Series: Series containing the count of policies in each chunk of the specified frequency.

    Notes:
        This function takes in policy level data as a Pandas DataFrame with a 'date' column
        indicating when each policy was created. It also takes a frequency parameter
        ('monthly', 'quarterly', or 'yearly') to specify how the data should be chunked.
        It then counts the number of policies within each chunk of the specified frequency
        across the timespan covered by the data. If no data exists for a particular chunk
        (e.g., an agent hadn't started working yet), it fills in np.nan.

    """

    # Convert 'date' column to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(policy_data['date']):
        policy_data['date'] = pd.to_datetime(policy_data['date'])

    # Set up date range based on frequency
    if frequency == 'monthly':
        date_range = pd.date_range(policy_data['date'].min(), policy_data['date'].max() + pd.offsets.MonthEnd(1), freq='MS')
    elif frequency == 'quarterly':
        date_range = pd.date_range(start=policy_data['date'].min(), end=policy_data['date'].max(), freq='QS')
    elif frequency == 'yearly':
        date_range = pd.date_range(start=policy_data['date'].min(), end=policy_data['date'].max(), freq='YS')
    else:
        raise ValueError("Invalid frequency. Please choose from 'monthly', 'quarterly', or 'yearly'.")

    # Count policies in each chunk
    policy_counts = []
    for start_date, end_date in zip(date_range, date_range[1:].append(pd.to_datetime([policy_data['date'].max()]))):
        # Handle edge case for the last chunk
        if start_date == end_date:
            count = policy_data[(policy_data['date'] == start_date)].shape[0]
        else:
            count = policy_data[(policy_data['date'] >= start_date) & (policy_data['date'] < end_date)].shape[0]
        policy_counts.append(count)

    return pd.Series(policy_counts, index=date_range)

if __name__ == '__main__':

    from app.routers.data_analysis_router import AgentAnalysisRequestData
    payload = AgentAnalysisRequestData(
                name="agent_analysis",
                period={
                    "unit" : 'months',
                    "value": 12,
                    "frequency": 'M'
                }
    )
    
    resp = get_agent_analysis(payload)
    print(resp)