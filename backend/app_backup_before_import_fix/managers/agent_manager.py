from app.registry.agent_registry import AgentRegistry


class AgentManager:

    def __init__(self):
        self.registry = AgentRegistry()
        self.instances = {}

    def list_agents(self):
        return self.registry.list()

    def get_agent(self, name: str):
        if name in self.instances:
            return self.instances[name]

        agent_class = self.registry.get(name)

        if agent_class is None:
            return None

        # Registry returns the class; manager owns instantiation.
        agent = agent_class()

        self.instances[name] = agent
        return agent

    async def execute(self, agent_name: str, task: str):

        agent = self.get_agent(agent_name)

        if agent is None:
            raise ValueError(f"Agent '{agent_name}' not found.")

        return await agent.run(task)

    def reset(self):
        self.instances.clear()