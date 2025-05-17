
import logging
import re

from datetime import datetime
from typing import Optional, List
from application.models.indicator_response import IndicatorResponse

logger = logging.getLogger(__name__)

def selector(text: str) -> Optional[str]:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    pattern = r'Option: ([ABCD])'
    match = re.search(pattern, text)
    if match: 
        return match.group(1)
    else:
        return None

def performance(text: str) -> Optional[str]:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    # NOTE Considering "unspecified" as option C (generally abnormal). Could improve prompt to handle this in the future
    pattern = r'Option: ([AB])'
    match = re.search(pattern, text)
    if match: 
        return match.group(1)
    else:
        return 'C'

def metric(text: str) -> str:
    if not text:
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    pattern = r'Metric: (.*)\s*-'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    else:
        logger.warning(f'Text "{text}" did not match metric regex pattern')
        return None

def frequency(text: str) -> str:
    if not text:
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    pattern = r'Frequency: (.*)\s*-'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip().lower()
    else:
        logger.warning(f'Text "{text}" did not match metric regex pattern')
        return None

def yes_or_no(text: str, keyword: str) -> Optional[bool]:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    pattern = fr'{keyword}: (Yes|No)\s*-\s*"(.*?)"'
    match = re.search(pattern, text)
    if match:
        match_text = match.group(1)
        if match_text.lower() == 'yes':
            return True
        else:
            return False
    else:
        return None

def date(text: str):
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None

    start_date = date_value(text, keyword='Start')
    end_date = date_value(text, keyword='End')

    return start_date, end_date


def date_value(text:str, keyword:str):
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    if not keyword: 
        logger.warning('Value for keyword was None, issue upstream of extraction logic.')
        return None
    if keyword.lower() == 'start':
        pattern = r'Start:\s*(\d{2}-\d{2}-\d{4})\s*-\s*"([^"]*)"'
    else: 
        pattern = r'End:\s*(\d{2}-\d{2}-\d{4})\s*-\s*"([^"]*)"'
    match = re.search(pattern, text)
    if match:
        match_text = match.group(1)
        try:
            date = datetime.strptime(match_text, '%m-%d-%Y')
            return date
        except ValueError:
            logger.warning(f'Unable to convert text "{text}" to date format yyyy/mm/dd.')

    return None

def amount_value(text: str, range: str) -> Optional[int]:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    if not range: 
        logger.warning('Value for range was None, issue upstream of extraction logic.')
        return None
    if range.lower() == 'between':
        pattern = r'Amount:\s+(\d+)\s+to\s+(\d+)\s+-\s+"([^"]*)"' # TODO Make sure this can handle empty quotation 
        match = re.search(pattern, text)
        if match: 
            val1_raw = match.group(1)
            val2_raw = match.group(2)
            try:
                val1 = int(val1_raw)
                val2 = int(val2_raw)
                return (val1, val2)
            except ValueError:
                logger.warning(f'Unable to convert text "{text}" to date format yyyy/mm/dd.')

            return None
            
    else:
        pattern = r'Amount:\s+(\d+)\s+-\s+"([^"]*)"'
        match = re.search(pattern, text)
        if match:
            match_text = match.group(1)
            try:
                val = int(match_text)
                return val
            except ValueError:
                logger.warning(f'Unable to convert text "{text}" to date format yyyy/mm/dd.')

        return None

def amount_range(text: str) -> str:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None

    pattern = r'Range:\s*(Above|Below|Between)\s*-\s*"(.*?)"'
    match = re.search(pattern, text)
    if match: 
        match_text = match.group(1)
        return match_text
    
    return None

def extract_status(text: str) -> str:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None

    pattern = r'Status:\s*(Inforce|Pending|Both)\s*-\s*"([^"]*)"'
    match = re.search(pattern, text)
    if match: 
        match_text = match.group(1)
        return match_text

    return None


def extract_premium(text: str) -> str:
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None

    lower_bound = premium_value(text, keyword='Lower')
    upper_bound = premium_value(text, keyword='Upper')

    return (lower_bound, upper_bound)


def premium_value(text: str, keyword:str):
    if not text: 
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return None
    if not keyword: 
        logger.warning('Value for keyword was None, issue upstream of extraction logic.')
        return None
    pattern = rf'{keyword}:\s*(\d+)\s*-\s*"([^"]*)"'
    match = re.search(pattern, text)
    if match:
        match_text = match.group(1)
        try:
            return int(match_text)
        except ValueError:
            logger.warning(f'Unable to convert text "{match_text}" to integer.')

    return None


def indicator_extraction(text:str) -> List[str]:

    phrases = ["Have Written", "Policy Status", "Policy Premium", "Policy Date", "Face Amount"]
    indicator_response = IndicatorResponse()

    if not text:  
        logger.warning('Value for text was None, issue upstream of extraction logic.')
        return indicator_response

    for phrase in phrases:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        attr_name = re.sub(r'\s+', '_', phrase.lower())
        if pattern.search(text):
            setattr(indicator_response, attr_name, True)
        else:
            setattr(indicator_response, attr_name, False)
    
    return indicator_response

if __name__ == '__main__':
    
    # test_input = """
    #     Range: Between - "since the beginning of last year"
    #     Date: 2023-01-01 to 2023-12-31 - "since the beginning of last year"
    # """

    # range_val = date_range(test_input)
    # date_val = date_value(test_input, range_val)
    # print(range_val)
    # print(date_val)

    # test_amount_value = 'Amount: 250000 to 500000 - ""'
    # resp = amount_value(test_amount_value,'between')
    # print(resp)
    
    # test_date_value = 'Date: 2023-01-01 to 2023-01-31 - ""'
    # resp = date_value(test_date_value,'between')
    # print(resp)

    # date_value_test = 'Start: 01-01-2024 - "since Jan 1, 2024"'
    # date_value_test = 'Start: 10-01-2023 - "during Q4 of 2023."'
    # resp = date_value_q3(date_value_test, 'Start')
    # print(resp)

    test = 'Start: 01-01-2022 - ""\nEnd: 03-04-2024 - ""'

