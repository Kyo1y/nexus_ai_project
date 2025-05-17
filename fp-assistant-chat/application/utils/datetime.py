from datetime import datetime

def datetime_to_str(datetime_obj: datetime) -> str:
    """Convert datetime object into string representation using format Year-Month-Day Hour:Minute:Second

    Args:
        datetime_obj (datetime): datetime to convert

    Returns:
        str: string representation
    """
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

def str_to_datetime(datetime_str: str) -> datetime:
    """Convert string to datetime object. Assumes representation is Year-Month-Day Hour:Minute:Second

    Args:
        datetime_str (str): datetime string to convert

    Returns:
        datetime: datetime object of given time
    """
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
