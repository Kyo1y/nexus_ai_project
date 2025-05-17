import pandas as pd 
import numpy as np

frequency_multipliers = {
    1: 1,      # Annually
    4: 12,     # Monthly
    3: 4,      # Quarterly
    2: 2,      # Semi-Annually
    9: 1,      # Single Payment
    12: 13,    # Every 4 weeks (52 weeks in a year / 4)
    7: 26,     # Bi-weekly (52 weeks in a year / 2)
    5: 24      # Semi-Monthly (12 months * 2)
}

# Function to calculate the annual premium
def calculate_annual_premium(row):
    premium = row['PAMT']
    frequency = row['BLLNG_FREQ_CD']
    multiplier = frequency_multipliers.get(frequency, 0) # default to 0 if frequency code is not found
    annual_premium = premium * multiplier
    return annual_premium

def fix_pid(pid):
    if len(str(pid)) == 10:
        return str(pid)
    elif len(str(pid)) == 7: 
        return '00' + str(pid) + '0'
    elif len(str(pid)) == 8:
        return '00' + str(pid)
    else:
        return str(pid)

isdt_filters = {
    '<1960':(1, 100), # Come back to this
    '1960':(1, 3500),
    '1970':(6, 9000),
    '1980':(10, 10000),
    '1990':(30, 30000),
    '2000':(30, 30000),
    '2010':(50, 50000),
    '>2010':(50, 50000)
}

def get_decade_value(date):
    year = date.year  # Ensure `date` is a datetime object
    if np.isnan(year):
        return '2010'

    if year < 1960:
        return '<1960'
    elif year > 2010:
        return '>2010'
    else:
        # Calculate the decade
        decade_start = (year // 10) * 10
        return str(decade_start)

def filter_annual_premium(val, isdt):
    decade_val = get_decade_value(isdt)
    accepted_range = isdt_filters[decade_val]
    if not accepted_range[0] < val < accepted_range[1]:
        return np.nan
    else:
        return val

qc_path = '/Users/brapp/fp-assistant/app/data_manager/agents/pcs_deduped.csv'
pcsr_path = '/Users/brapp/Downloads/Ben_PCS_Data.txt' # Inforce 
lnb_path = '/Users/brapp/Downloads/LNB_Extract_for_Ben 2.txt' # Pending

pcsr_df = pd.read_csv(pcsr_path, delimiter='|')
lnb_df = pd.read_csv(lnb_path, delimiter='|')
qc_df = pd.read_csv(qc_path)

pcsr_df['PID'] = pcsr_df['PID'].apply(fix_pid)
lnb_df['PID'] = lnb_df['PID'].apply(fix_pid)
qc_df['pid'] = qc_df['pid'].apply(fix_pid)

pcs_joined = pd.concat([pcsr_df, lnb_df])
pcs_joined = pcs_joined.sort_values(by=['PID', 'SOURCE'], key=lambda col: col=='SOURCE')
pcs_joined = pcs_joined.drop_duplicates(subset='PID', keep='first')

# Calculate percentage of face amount
    # If premium is null, return null 
    # If face amount is null, check to see if premium is in an acceptable general range 
    # Need more info to handle premiums with a one-time payment

pcs_joined['calculated_annual_premium'] = pcs_joined[['PAMT', 'BLLNG_FREQ_CD']].apply(calculate_annual_premium, axis=1)
qc_df_with_pcsr_premium = qc_df.merge(pcs_joined[['PID', 'calculated_annual_premium']], left_on='pid', right_on='PID', how='left')
qc_df_with_pcsr_premium = qc_df_with_pcsr_premium.merge(pcs_joined[['PID', 'PAMT', 'BLLNG_FREQ_CD']], left_on='pid', right_on='PID', how='left', suffixes=('_QC', '_PCSR'))
qc_df_with_pcsr_premium['isdt'] = pd.to_datetime(qc_df_with_pcsr_premium['isdt'])

# Treat Annual Premium 
qc_df_with_pcsr_premium['calculated_annual_premium_filtered'] = qc_df_with_pcsr_premium[['isdt', 'calculated_annual_premium']].apply(lambda x: filter_annual_premium(x['calculated_annual_premium'], x['isdt']), axis=1)
qc_df_with_pcsr_premium['calculated_premium_ratio'] = qc_df_with_pcsr_premium['calculated_annual_premium_filtered'] / qc_df_with_pcsr_premium['famt']
qc_df_with_pcsr_premium['acceptable_ratio'] = qc_df_with_pcsr_premium['calculated_premium_ratio'] > 0.002 or qc_df_with_pcsr_premium['calculated_premium_ratio'] < 1
qc_df_with_pcsr_premium.to_csv('pcs_premium_calc.csv', index=False)
print("Done.")