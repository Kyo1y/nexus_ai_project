
import datetime
import logging

from dataclasses import dataclass, field
from typing import Optional, Union, get_args, get_origin

logger = logging.getLogger(__name__)


class Agent:
    name: str
    agent: Optional[str] = None
    historical_average: Optional[float] = None
    current_volume: Optional[int] = None
    recent_faceamount: Optional[float] = None
    last_policy_date: Optional[datetime.datetime] = None
    count_pid: Optional[int] = None
    min_pid: Optional[int] = None
    max_pid: Optional[int] = None
    label: Optional[str] = None

    min_isdt: Optional[datetime.datetime] = None
    max_isdt: Optional[datetime.datetime] = None
    
    min_famt: Optional[float] = None
    max_famt: Optional[float] = None
    mean_famt: Optional[float] = None
    total_famt: Optional[float] = None

    min_apamt: Optional[float] = None
    max_apamt: Optional[float] = None
    mean_apamt: Optional[float] = None
    total_annual_premiums: Optional[float] = None

    def __init__(self, **kwargs):
        self.found_keys = []
        for key, value in kwargs.items():
            self.found_keys.append(key)
            setattr(self, key, value)



    @property
    def confidence(self):
        # TODO: fix fake confidence
        return 'high' if self.label else None

    @classmethod
    def get_kwarg_types(cls):
         # Convert types as needed
        update_type = {}
        for attr_name, types in cls.__annotations__.items():
            if get_origin(types) is Union:
                arg_types = get_args(types)
                not_none_types = [at for at in arg_types if at is not type(None)]
                if len(not_none_types) == 1:
                    update_type[attr_name] = not_none_types[0]
                else:
                    logger.warning(f'Unable to determine type for union {attr_name}, no auto update available.')
                    pass
            else:
                if isinstance(types, type):
                    update_type[attr_name] = types
                else:
                    logger.warning(f'Unable to determine type for singular {attr_name}, no auto update available.')
                    pass
        return update_type
    
    def json(self):
        # TODO: auto generate from field names
        json_repr = {
            'name': self.name,
            'agent': self.agent,
            'historical_average': self.historical_average,
            'current_volume': self.current_volume,
            'recent_faceamount': self.recent_faceamount,
            'last_policy_date': self.last_policy_date,
            'label': self.label,
            'confidence': 'high' if self.label is not None else None,
            **{key: getattr(self, key, None) for key in self.found_keys if key != 'agent'}
        }
        json_repr = {k: v for k, v in json_repr.items() if v is not None}
        return json_repr
    
    # def row(self):
    #     row = [self.name]

    #     attr_order = [self.previous_performance, self.current_performance, self.label, 
    #                   self.recent_faceamount, 
    #                   self.last_policy_date, 
    #                   self.confidence]
        
    #     for attribute in attr_order:
    #         if attribute is not None:
    #             row.append(attribute)

    #     return row
    
    def row(self) -> list:
        attr_order = ['name', 'previous_volume', 'current_volume', 'label', 'recent_faceamount', 'last_policy_date', 'confidence']

        formatted_values = []

        for variable_name in attr_order:
            attr_value = getattr(self, variable_name)
            if attr_value is not None:
                if isinstance(attr_value, datetime.datetime):
                    formatted_values.append(datetime.datetime.strftime(attr_value, "%Y-%m-%d"))
                elif isinstance(attr_value, float):
                    if variable_name == "recent_faceamount":
                        formatted_values.append(f"${attr_value:,.2f}")
                    else:
                        formatted_values.append(f"{attr_value:.2f}")
                else:
                    formatted_values.append(str(attr_value))

        return formatted_values
