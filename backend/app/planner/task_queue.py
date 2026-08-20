from typing import List
from app.planner.task import Task


class TaskQueue:

    def __init__(self):
        self.tasks: List[Task] = []

    def add(self, task: Task):
        self.tasks.append(task)

    def pending(self):
        return [t for t in self.tasks if t.status == "Pending"]

    def completed(self):
        return [t for t in self.tasks if t.status == "Completed"]

    def running(self):
        return [t for t in self.tasks if t.status == "Running"]

    def get(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_status(self, task_id, status):
        task = self.get(task_id)
        if task:
            task.status = status

    def all(self):
        return self.tasks

