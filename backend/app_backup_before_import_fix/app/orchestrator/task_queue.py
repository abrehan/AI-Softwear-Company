class TaskQueue:

    def __init__(self):
        self.tasks = []

    def add(self, agent, task):
        self.tasks.append({
            "agent": agent,
            "task": task
        })

    def next(self):
        if self.tasks:
            return self.tasks.pop(0)
        return None
