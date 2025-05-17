
import datetime



from dataclasses import dataclass, field
from dateutil.relativedelta import relativedelta
from enum import Enum
from typing import Any, Literal, Optional, Dict, List, Union, Tuple

from application.utils.datetime import datetime_to_str

@dataclass
class Period:
    start: Optional[datetime.datetime] = None
    end: Optional[datetime.datetime] = None
    interval: Optional[relativedelta] = None
    frequency: Optional[Literal["monthly", "quarterly"]] = None

    def __str__(self):
        # start_formatted = self.start.strftime("%Y-%m-%d")
        # end_formatted = self.end.strftime("%Y-%m-%d")
        # return f"{start_formatted} to {end_formatted}"
        start = self.start.strftime("%B %Y")
        
        end = self.end.strftime("%B %Y")
        return f"{start} to {end}"


class QueryType(Enum):
    PERFORMANCE = 'A'
    NOT_WRITTEN = 'B'
    AGENT_AMOUNT = 'C'
    SQL =  'SQL'
    EXPLAIN = 'D'
    OOS = 'Unspecified'  # Out of Scope

class PerformanceVolumeType(Enum):
    HIGH = 'A'
    LOW = 'B'
    BOTH = 'C'
    UNSPECIFIED = 'Unspecified'

@dataclass
class Assumptions:
    volume: Optional[PerformanceVolumeType]
    period: Optional[Period] = None


class BaseQuery:
    assumptions: Optional[Assumptions] = None

    def build_payload(self) -> Dict[str, Any]:
        raise NotImplementedError(f'Build Payload has not been built yet, be sure to implement in subclass {self.__class__.__name__}.')

@dataclass
class PerformanceQuery(BaseQuery):
    volume: PerformanceVolumeType
    metric: str
    period: Optional[Period] = None

    def build_payload(self) -> Dict[str, Any]:
        start = datetime_to_str(self.period.start) if self.period.start else None
        end = datetime_to_str(self.period.end) if self.period.end else None
        payload = {
            'name': 'agent_analysis',
            'start': start,
            'end': end,
            'frequency': self.period.frequency,
            'metric': self.metric
        }
        return payload

@dataclass
class NotWrittenQuery(BaseQuery):
    negation: bool
    date: Union[datetime.datetime, Tuple[datetime.datetime, datetime.datetime]] = datetime.datetime(2023,1,1)
    range: Literal["After", "Before", "Between"] = "Before"
    negation: bool = True  # TODO: sync up on theis variable

    def build_payload(self) -> Dict[str, Any]:
        group_filter_dict = {'field': 'isdt'}
        if self.range == 'After':
            group_filter_dict['lower'] = self.date.strftime('%Y-%m-%d')
        elif self.range == 'Before':
            group_filter_dict['upper'] = self.date.strftime('%Y-%m-%d')
        elif self.range == 'Between':
            group_filter_dict['lower'], group_filter_dict['upper'] = [d.strftime('%Y-%m-%d') for d in self.date]
        else:
            raise ValueError(f'Unsure how to handle amount_range being {self.range}')

        json_payload = {
            "filters": [],
            "grouping": {
                "by": "agent",
                "negate": self.negation
            },
            "aggregate": {
                "on": "isdt",
                "how": "max"
            },
            "group_filters": [
                group_filter_dict
            ]
        }
        return json_payload

@dataclass
class AgentAmountQuery(BaseQuery):
    amount_range: Literal["Above", "Below", "Between"]
    amount_value: Union[int, Tuple[int, int]]
    negation:bool
    date_value: Union[datetime.datetime, Tuple[datetime.datetime, datetime.datetime]] = datetime.datetime(2023,1,1)
    date_range: Literal["After", "Before", "Between"] = "Before"
    negation: bool = False

    def build_payload(self) -> Dict[str, Any]:
        # Set up filter dict for amount
        filter_dict = {'field': 'isdt'}
        if self.date_range == 'After':
            filter_dict['lower'] = self.date_value.strftime('%Y-%m-%d')
        elif self.date_range == 'Before':
            filter_dict['upper'] = self.date_value.strftime('%Y-%m-%d')
        elif self.date_range == 'Between':
            filter_dict['lower'], filter_dict['upper'] = [d.strftime('%Y-%m-%d') for d in self.date_value]
        else:
            raise ValueError(f'Unsure how to handle amount_range being {self.date_range}')

        group_filter_dict = {'field': 'famt'}
        if self.amount_range == 'Above':
            group_filter_dict['lower'] = self.amount_value
        elif self.amount_range == 'Below':
            group_filter_dict['upper'] = self.amount_value
        elif self.amount_range == 'Between':
            group_filter_dict['lower'], group_filter_dict['upper'] = self.amount_value
        else:
            raise ValueError(f'Unsure how to handle amount_range being {self.amount_range}')

        json_payload = {
            "filters": [
                filter_dict
            ],
            "grouping": {
                "by": "agent",
                "negate": self.negation
            },
            "aggregate": {
                "on": "famt",
                "how": "max"
            },
            "group_filters": [
                group_filter_dict
            ]
        }
        return json_payload

@dataclass
class OOSQuery(BaseQuery): pass

@dataclass
class ExplainQuery(BaseQuery): pass

class Query:
    # Reference to types
    query_type: QueryType
    
    # Add reference to Query object
    performance = PerformanceQuery
    not_written = NotWrittenQuery
    agent_amount = AgentAmountQuery
    oos = OOSQuery
    explain = ExplainQuery


def convert_str(value: str):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()
    except:
        if '.' in value:
            try:
                return float(value)
            except:
                return value
        else:
            try:
                return int(value)
            except:
                return value

    return value

class Range:
    field: str
    upper: Union[datetime.date, int, float, None] = None
    lower: Union[datetime.date, int, float, None] = None
    flip: bool = False
    dtype: type = None

    def __init__(self,
                 field: str,
                 lower: Union[datetime.date, int, float, None] = None, 
                 upper: Union[datetime.date, int, float, None] = None, 
                 flip: bool = False):
        if not (upper or lower):
            raise TypeError('__init__() must have either "upper" or "lower" provided')
        elif flip and not (upper and lower):
            raise TypeError('Should only use flip when "upper and "lower" are both passed. Flip reverses the logic so just change argument.')


        if isinstance(upper, str):
            self.upper = convert_str(upper)
        else:
            self.upper = upper
       
        if isinstance(lower, str):
            self.lower = convert_str(lower)
        else:
            self.lower = lower

        self.flip = flip
        self.field = field

        if self.upper:
            self.dtype = type(self.upper)
        elif self.lower:
            self.dtype = type(self.lower)

    def negate(self):
        if self.upper and self.lower:
            self.flip = not self.flip
        elif self.upper:
            self.lower = self.upper
            self.upper = None
        elif self.lower:
            self.upper = self.lower
            self.lower = None
    
    def __str__(self):
        args = f'field={self.field}, lower={self.lower}, upper={self.upper}, flip={self.flip}, dtype={self.dtype}'
        return f'{self.__class__.__name__}({args})'

    def __repr__(self) -> str:
        return self.__str__()
    
    def payload(self):
        if self.dtype is datetime.date:

            json = {
                'field': self.field,
                'lower': self.lower.strftime('%Y-%m-%d') if self.lower else None,
                'upper': self.upper.strftime('%Y-%m-%d') if self.upper else None,
            }
        else:
            json = {
                'field': self.field,
                'lower': self.lower,
                'upper': self.upper,
            }
        return json

class Value:
    field: str
    items: List[Any]
    negate: bool = False
    dtype: type = None

    def __init__(self, field: str, items: List[str], negate: bool = False):
        self.items = items
        self.field = field
        self.negate = negate
        if self.items:
            self.dtype = type(self.items[0])
        else:
            self.dtype = None

    def __str__(self):
        args = f'field={self.field}, items={self.items}, negate={self.negate} dtype={self.dtype}'
        return f'{self.__class__.__name__}({args})'

    def __repr__(self) -> str:
        return self.__str__()
    
    def payload(self):
        json = {
            'field': self.field,
            'items': self.items,
            'negate': self.negate
        }
        return json


class NewQuery:
    written: bool
    status: Literal['inforce', 'pending', 'both']
    premium: Optional[Range] = None
    date: Optional[Range] = None
    face_amount: Optional[Range] = None

    def payload(self):

        filter_objects = [self.premium, self.date, self.face_amount]
        filter_objects = [filt_obj for filt_obj in filter_objects if filt_obj is not None]

        {
            "filters": [
                filter_objects
            ],
            "grouping": {
                "by": "agent",
            },
            "aggregate": {
                "on": "famt",
                "how": "max"
            },
            "group_filters": [
                group_filter_dict
            ]
        }
