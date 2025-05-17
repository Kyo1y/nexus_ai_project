"""Payload to hold information from response"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from application.models.query import Query
from application.models.requests.agent import Agent

@dataclass
class Response:
    query: Optional[Query] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    results: List[Agent] = field(default_factory=list)
    dtypes: Dict[str, str] = field(default_factory=dict)
