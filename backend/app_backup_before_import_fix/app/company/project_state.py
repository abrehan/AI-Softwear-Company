class ProjectState:

    def __init__(self):
        self.status = "Idle"
        self.current_task = None
        self.completed = 0
        self.failed = 0

    def start(self):
        self.status = "Running"

    def finish(self):
        self.status = "Completed"

    def error(self):
        self.status = "Failed"

    def set_task(self, task):
        self.current_task = task
