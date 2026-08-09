from app.registry.agent_registry import AgentRegistry


class AgentManager:

    def __init__(self):
        self.registry = AgentRegistry()
        self.instances = {}

    def list_agents(self):
        return self.registry.list()

    def get_agent(self, name):

        if name in self.instances:
            return self.instances[name]

        agent = self.registry.get(name)

        if agent is None:
            return None

        self.instances[name] = agent
        return agent

    async def execute(self, agent_name, task):

        agent = self.get_agent(agent_name)

        if agent is None:
            raise Exception(f"{agent_name} not found")

        return await agent.run(task)

    def reset(self):
        self.instances.clear()