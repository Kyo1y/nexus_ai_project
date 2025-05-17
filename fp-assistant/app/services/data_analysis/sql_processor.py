import json
import logging

import duckdb
import pandas as pd

from app.data_manager import datamanager
from app.data_manager.datamanager import map_agent_status_to_agent_code

logger = logging.getLogger(__name__)

def fix_column_names(df):

    df.columns = df.columns.lower()

    if "max(isdt)" in df.columns:
        df.rename({'max(isdt)'}, axis=1)

    return 

async def sql_processing(sql_statement: str):
    # TODO: can add code to ensure that FROM line match variable name and potentially update if need be
    # Request data
    policy_data = datamanager.collect()
    # Make any needed updates to df
    # if 'source' not in sql_statement:
    #     policy_data = policy_data[policy_data['source'] == 'inforce']

    # Ensure types for datetime
    if 'isdt' in policy_data.columns and pd.api.types.is_object_dtype(policy_data['isdt']):
        try:
            policy_data['isdt'] = pd.to_datetime(policy_data['isdt'])
            policy_data['isdt'] = policy_data['isdt'].dt.tz_localize(None)
        except:
            logger.exception('Unable to convert isdt to datetime')

    duckdb.execute("SET TIMEZONE='UTC'")
    results = duckdb.query(sql_statement).to_df()

    float_cols = results.select_dtypes(include=['float']).columns
    results[float_cols] = results[float_cols].round(2)

    # Datetime cols
    date_cols = results.select_dtypes(include=['datetime', 'datetimetz']).columns
    for col in date_cols:
        results[col] = results[col].dt.strftime('%Y-%m-%d')

    # First, check if results has everything we need to be able to map activity properly 
    # Then, map onto results
    if 'agent' in results.columns:
        results = map_agent_status_to_agent_code(results)
    
    # results = fix_column_names(results)
    results = results.dropna()
    try:
        results = results.sort_values(by='name')
    except Exception as e: 
        logger.exception("name not found in results, could not sort: ", e)

    
    return {
        "count" : len(results),
        "agent_list": json.loads(results.to_json(orient='records')),
        "dtypes": results.dtypes.astype(str).to_dict()
        }

if __name__ == '__main__':
    sql_query = """
        SELECT agent
        FROM policy_data
        WHERE famt > 75000 AND isdt >= '1970-01-01'
    """


    # response = sql_processing(sql_query)
    # print(response)


    # # import pandas as pd 
    # df = pd.read_csv('/Users/brapp/fp-assistant-chat/fp-assistant-chat/application/querier/test_examples_may24.csv')
    # for i, row in df.iterrows(): 
    #     print(i)
    #     sql_text = row['validated_sql_statement']
    #     results = sql_processing(sql_text)
        
    #     # query = SQLQuery(sql_text)
    #     # print(query.original_text)
    #     df.at[i, 'duckdb_count'] = results['count']

    # df.to_csv('/Users/brapp/fp-assistant-chat/fp-assistant-chat/application/querier/test_examples_may24.csv')

    # sql_query = """
    #     SELECT agent, name, AVG(famt) as avg_famt, AVG(apamt) as avg_apamt, COUNT(pid)/((julian(CAST('2024-05-24' AS DATE)) - julian(MIN(isdt)))/365.25) as avg_policy_per_year
    #     FROM policy_data
    #     WHERE prim_ofcd = 'B56' GROUP BY agent, name
    #     HAVING avg_famt > 100000 AND avg_apamt > 50 AND avg_policy_per_year >= 10
    # """

    response = sql_processing(sql_query)
    print(response)