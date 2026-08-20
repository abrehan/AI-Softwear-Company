import asyncio
from app.managers.agent_manager import AgentManager


class Company:

    def __init__(self):
        self.manager = AgentManager()

    async def execute_project(self, task: str):

        print("ðŸ¢ AI Company Started")

        agents = self.manager.list_agents()

        print("Registered Agents:", agents)
        print("Total Agents:", len(agents)) 

        semaphore = asyncio.Semaphore(3)

        async def run_agent(agent_name):

            async with semaphore:

                print(f"ðŸš€ Starting {agent_name.upper()} Agent...")

                try:
                    result = await self.manager.execute(agent_name, task)

                    print(f"âœ… Finished {agent_name.upper()} Agent")

                    return agent_name, result

                except Exception as e:

                    print(f"âŒ {agent_name.upper()} Error:", e)

                    return agent_name, str(e)

        tasks = [run_agent(agent) for agent in agents]

        results = await asyncio.gather(*tasks)

        return {name: result for name, result in results}

