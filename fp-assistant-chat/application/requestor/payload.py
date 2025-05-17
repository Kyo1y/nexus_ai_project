import datetime

from dataclasses import dataclass, asdict
from typing import Any, Dict

@dataclass
class FCSPCSDataPayload:
    field_office_code: str 
    start_date: datetime.datetime
    end_date: datetime.datetime

    std_unit: float = 1.0
    get_offices_only: bool = False
    rows: int = 1000
    output_file_name: str = 'data.xlsx'
    output_format: str = 'xlsx'
    month_interval: int = 1

    def dict(self) -> Dict[str, Any]:
        return {k: str(v) for k, v in asdict(self).items()}
