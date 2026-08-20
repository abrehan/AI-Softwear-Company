from dataclasses import dataclass
from app.board.task_status import TaskStatus


@dataclass
class Task:

    id: int

    title: str

    department: str

    description: str

    status: TaskStatus = TaskStatus.TODO

    assigned_to: str = ""

    result: str = ""

