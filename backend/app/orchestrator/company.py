import asyncio

from app.managers.agent_manager import AgentManager
from app.workflow.dependency_graph import DEPENDENCIES


class Company:

    def __init__(self):
        self.manager = AgentManager()

    async def execute_project(self, task: str):

        print("🏢 AI Company Started")

        self.manager.reset()     # <-- ADD THIS

        completed = set()
        results = {}

        while len(completed) < len(DEPENDENCIES):

            runnable = []

            for agent, deps in DEPENDENCIES.items():

                if agent in completed:
                    continue

                if all(dep in completed for dep in deps):
                    runnable.append(agent)

            if not runnable:
                print("❌ Dependency graph is blocked.")
                break

            print("\n====================================")
            print("Running:", ", ".join(runnable))
            print("====================================")

            jobs = [
                self.run_agent(agent, task)
                for agent in runnable
            ]

            outputs = await asyncio.gather(
                *jobs,
                return_exceptions=True
            )

            for agent, output in zip(runnable, outputs):

                if isinstance(output, Exception):

                    print(f"❌ {agent.upper()} failed")
                    print(output)

                else:

                    print(f"✅ {agent.upper()} completed")

                    completed.add(agent)

                    results[agent] = output

        print("\n🎉 PROJECT COMPLETE")

        return results

    async def run_agent(self, agent_name, task):

        print(f"🚀 Starting {agent_name.upper()} Agent...")

        result = await self.manager.execute(
            agent_name,
            task
        )

        return result