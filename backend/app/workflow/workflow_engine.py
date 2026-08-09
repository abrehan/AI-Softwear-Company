import asyncio

from app.registry.agent_registry import AgentRegistry
from app.workflow.dependency_graph import DEPENDENCIES


class WorkflowEngine:

    def __init__(self):

        self.registry = AgentRegistry()

        self.completed = set()

        self.failed = set()

    async def execute(self, project: str):

        print("=" * 60)
        print("🚀 AI SOFTWARE COMPANY STARTED")
        print("=" * 60)

        while len(self.completed) < len(DEPENDENCIES):

            runnable = []

            for agent_name, deps in DEPENDENCIES.items():

                if agent_name in self.completed:
                    continue

                if agent_name in self.failed:
                    continue

                if all(dep in self.completed for dep in deps):
                    runnable.append(agent_name)

            if not runnable:

                print("❌ No runnable agents remaining.")
                break

            tasks = []

            for name in runnable:

                agent = self.registry.get(name)

                print()
                print("=" * 36)
                print(f"Running: {name}")
                print("=" * 36)

                tasks.append(
                    self.run_agent(name, agent, project)
                )

            await asyncio.gather(*tasks)

        print()
        print("=" * 60)
        print("🎉 WORKFLOW FINISHED")
        print("=" * 60)

        print(f"Completed: {len(self.completed)}")
        print(f"Failed: {len(self.failed)}")

        return list(self.completed)

    async def run_agent(
        self,
        name,
        agent,
        project
    ):

        try:

            await agent.run(project)

            self.completed.add(name)

            print(f"✅ {name} completed")

        except Exception as e:

            self.failed.add(name)

            print(f"❌ {name} failed")

            print(e)