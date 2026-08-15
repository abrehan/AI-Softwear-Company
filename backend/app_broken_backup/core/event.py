from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:

    source: str

    event_type: str

    data: dict

    timestamp: datetime