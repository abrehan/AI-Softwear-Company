from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    id: int
    title: str
    description: str
    agent: str
    priority: str = "Medium"
    status: str = "Pending"
    depends_on: List[int] = field(default_factory=list)
