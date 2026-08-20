class MemoryService:
    def __init__(self):
        self.data = {}

    def save(self, agent, task, result):
        self.data[agent] = {
            "task": task,
            "result": result
        }

    def get(self, agent):
        return self.data.get(agent)

    def all(self):
        return self.data


# ONE shared memory for the whole company
company_memory = MemoryService()