class DependencyGraph:

    def __init__(self):
        self.graph = {}

    def add(self, task_id, depends_on):
        self.graph[task_id] = depends_on

    def dependencies(self, task_id):
        return self.graph.get(task_id, [])

    def ready(self, task_id, queue):
        deps = self.dependencies(task_id)

        for dep in deps:
            task = queue.get(dep)

            if task is None:
                return False

            if task.status != "Completed":
                return False

        return True
