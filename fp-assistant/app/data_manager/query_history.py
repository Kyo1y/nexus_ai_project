import json
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Union

DATE_TIME_FMT = '%Y-%m-%dT%H:%M:%SZ'

class QueryLog:
    name: str
    last_run: Optional[datetime]
    run_interval: relativedelta

    def __init__(self, name: str, last_run: Union[str, datetime], run_interval: Optional[relativedelta] = None) -> None:
        self.name = name
        if isinstance(last_run, str):
            last_run = datetime.strptime(last_run, DATE_TIME_FMT)
        self.last_run = last_run
        
        if not run_interval:
            run_interval = relativedelta(days=1)
        self.run_interval = run_interval
    
    def ready_to_run(self):
        return self.last_run == None or self.last_run <= datetime.utcnow() - self.run_interval
    
    def ran(self):
        self.last_run = datetime.utcnow()

    @property
    def last_run_str(self):
        if self.last_run is None:
            return None

        return self.last_run.strftime(DATE_TIME_FMT)

class QueryHistory:
    FCS: QueryLog
    PCS: QueryLog
    run_interval: relativedelta
    history_json_path: str

    def __init__(self, history_json_path: Optional[str] = None, run_interval: Optional[relativedelta] = None) -> None:
        # Load in data
        curr_dir = os.path.dirname(__file__)
        if not history_json_path:
            history_json_path = os.path.join(curr_dir, 'agents/query_history.json')
        self.history_json_path = history_json_path

        if os.path.isfile(self.history_json_path):
            with open(self.history_json_path, 'r') as f:
                history_json = json.load(f)
                self.FCS = QueryLog('fcs', history_json.get('fcs', {}).get('last_run'), run_interval)
                self.PCS = QueryLog('pcs', history_json.get('pcs', {}).get('last_run'), run_interval)
        else:
            self.FCS = QueryLog('fcs', None, run_interval)
            self.PCS = QueryLog('pcs', None, run_interval)


    def save(self):
        json_state = {
            "fcs": {"last_run": self.FCS.last_run_str},
            "pcs": {"last_run": self.PCS.last_run_str}
        }

        with open(self.history_json_path, 'w') as f:
            json.dump(json_state, f, indent=4)