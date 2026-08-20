import asyncio
from typing import Any

from backend.app.managers.agent_manager import AgentManager
from backend.app.workflow.dependency_graph import DEPENDENCIES


class WorkflowEngine:

    def __init__(self):
        self.manager = AgentManager()
        self.completed: set[str] = set()
        self.failed: set[str] = set()
        self.results: dict[str, Any] = {}
        self.errors: dict[str, str] = {}

    async def execute(self, project: str):

        print("=" * 60)
        print("AI SOFTWARE COMPANY WORKFLOW STARTED")
        print("=" * 60)

        self.manager.reset()
        self.completed.clear()
        self.failed.clear()
        self.results.clear()
        self.errors.clear()

        while len(self.completed) + len(self.failed) < len(DEPENDENCIES):

            runnable = []

            for agent_name, deps in DEPENDENCIES.items():

                if agent_name in self.completed:
                    continue

                if agent_name in self.failed:
                    continue

                # A task may run only when every dependency completed.
                if all(dep in self.completed for dep in deps):
                    runnable.append(agent_name)

            if not runnable:
                print("No runnable agents remaining.")
                break

            print()
            print("=" * 60)
            print("RUNNING:", ", ".join(runnable))
            print("=" * 60)

            tasks = [
                self.run_agent(agent_name, project)
                for agent_name in runnable
            ]

            await asyncio.gather(*tasks)

        # Mark agents whose dependency chain can no longer complete.
        blocked = {
            name
            for name in DEPENDENCIES
            if name not in self.completed
            and name not in self.failed
        }

        for name in blocked:
            self.errors[name] = "Blocked by failed dependency."

        print()
        print("=" * 60)
        print("WORKFLOW FINISHED")
        print("=" * 60)
        print(f"Completed: {len(self.completed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Blocked: {len(blocked)}")

        return {
            "status": "completed" if not self.failed and not blocked else "partial",
            "completed": list(self.completed),
            "failed": self.errors,
            "results": self.results,
        }

    async def run_agent(self, agent_name: str, project: str):

        print(f"Starting {agent_name.upper()} Agent...")

        try:
            dependency_outputs = []

            for dependency in DEPENDENCIES.get(agent_name, []):
                output = self.results.get(dependency)

                if output:
                    dependency_outputs.append(
                        f"""
--- {dependency.upper()} OUTPUT ---
{output}
--- END {dependency.upper()} OUTPUT ---
"""
                    )

            context = "\n".join(dependency_outputs)

            task = f"""
ORIGINAL PROJECT REQUEST:
{project}

UPSTREAM AGENT RESULTS:
{context if context else "No upstream agent results yet."}

YOUR ROLE:
You are the {agent_name} agent.

Complete your responsibility for this project.
Use the upstream results as input.
Do not invent completed work.
Clearly distinguish facts, decisions, recommendations, and unknowns.
"""

            result = await self.manager.execute(
                agent_name,
                task
            )

            self.results[agent_name] = result
            self.completed.add(agent_name)

            print(f"{agent_name.upper()} completed.")

        except Exception as exc:

            self.failed.add(agent_name)
            self.errors[agent_name] = (
                f"{type(exc).__name__}: {exc}"
            )

            print(
                f"{agent_name.upper()} FAILED: "
                f"{type(exc).__name__}: {exc}"
            )
