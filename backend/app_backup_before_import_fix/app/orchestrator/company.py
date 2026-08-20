from backend.app.workflow.workflow_engine import WorkflowEngine


class Company:

    def __init__(self):
        self.engine = WorkflowEngine()

    async def execute_project(self, task: str):

        return await self.engine.execute(task)
