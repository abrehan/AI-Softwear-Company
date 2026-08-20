from app.managers.agent_manager import AgentManager


class WorkflowManager:

    def __init__(self):
        self.manager = AgentManager()

    async def execute_project(self, task: str):

        results = {}

        results["CEO"] = await self.manager.execute(
            "ceo",
            task
        )

        results["CTO"] = await self.manager.execute(
            "cto",
            task
        )

        results["Backend"] = await self.manager.execute(
            "backend",
            task
        )

        return results

