from backend.app.board.task import Task
from backend.app.board.task_status import TaskStatus


class TaskBoard:

    def __init__(self):

        self.tasks = []

        self.counter = 1

    def create(self, title, department, description):

        task = Task(

            id=self.counter,

            title=title,

            department=department,

            description=description

        )

        self.counter += 1

        self.tasks.append(task)

        print(f"ðŸ“‹ Task Created: {title}")

        return task

    def pending(self):

        return [

            task

            for task in self.tasks

            if task.status == TaskStatus.TODO

        ]

    def assign(self, task_id, agent):

        for task in self.tasks:

            if task.id == task_id:

                task.assigned_to = agent

                task.status = TaskStatus.IN_PROGRESS

    def complete(self, task_id, result):

        for task in self.tasks:

            if task.id == task_id:

                task.result = result

                task.status = TaskStatus.DONE

    def fail(self, task_id):

        for task in self.tasks:

            if task.id == task_id:

                task.status = TaskStatus.FAILED

    def review(self, task_id):

        for task in self.tasks:

            if task.id == task_id:

                task.status = TaskStatus.REVIEW

    def all(self):

        return self.tasks


board = TaskBoard()
