import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def run_all_agents():
    print("=" * 70)
    print("🏢 RUNNING ALL VIRTUAL OFFICE AGENTS")
    print("=" * 70)
    print()
    
    # Define all agents to run
    agents_to_run = [
        ("CEO", "app.agents.ceo.ceo_agent", "CEOAgent"),
        ("PM", "app.agents.pm.pm_agent", "PMAgent"),
        ("CTO", "app.agents.cto.cto_agent", "CTOAgent"),
        ("Dev", "app.agents.dev.dev_agent", "DevAgent"),
        ("Frontend", "app.agents.frontend.frontend_agent", "FrontendAgent"),
        ("Backend", "app.agents.backend.backend_agent", "BackendAgent"),
        ("Database", "app.agents.database.database_agent", "DatabaseAgent"),
        ("DevOps", "app.agents.devops.devops_agent", "DevOpsAgent"),
        ("DevSecOps", "app.agents.devsecops.devsecops_agent", "DevSecOpsAgent"),
        ("CustomerSupport", "app.agents.customer_support.customer_support_agent", "CustomerSupportAgent"),
    ]
    
    test_task = "Build a multi-tenant hotel booking platform with payment processing and user authentication."
    
    results = {}
    
    for agent_name, module_path, class_name in agents_to_run:
        try:
            print(f"🔄 Running {agent_name} Agent...")
            
            # Import the agent
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent = agent_class()
            
            # Run the agent
            if hasattr(agent, 'analyze_project'):
                result = await agent.analyze_project(test_task)
            elif hasattr(agent, 'plan_project'):
                result = await agent.plan_project(test_task)
            elif hasattr(agent, 'design_architecture'):
                result = await agent.design_architecture(test_task)
            elif hasattr(agent, 'generate_code'):
                result = await agent.generate_code(test_task)
            elif hasattr(agent, 'develop_frontend'):
                result = await agent.develop_frontend(test_task)
            elif hasattr(agent, 'design_database'):
                result = await agent.design_database(test_task)
            elif hasattr(agent, 'deploy_project'):
                result = await agent.deploy_project(test_task)
            elif hasattr(agent, 'devsecops_strategy'):
                result = await agent.devsecops_strategy(test_task)
            elif hasattr(agent, 'customer_support'):
                result = await agent.customer_support(test_task)
            else:
                # Fallback to run method
                result = await agent.run(test_task)
            
            results[agent_name] = len(result) if result else 0
            print(f"✅ {agent_name} Agent complete ({len(result) if result else 0} chars)")
            print()
            
        except Exception as e:
            print(f"❌ {agent_name} Agent failed: {e}")
            print()
            continue
    
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    for agent, length in results.items():
        status = "✅" if length > 0 else "⚠️"
        print(f"{status} {agent}: {length} chars")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_all_agents())
