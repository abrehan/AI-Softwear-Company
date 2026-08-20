import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_agents():
    print("=" * 70)
    print("🚀 QUICK TEST: Selected Agents")
    print("=" * 70)
    print()
    
    task = "Build a hotel booking platform with payment processing."
    
    agents_to_test = [
        ("ceo", "CEOAgent"),
        ("pm", "PMAgent"),
        ("cto", "CTOAgent"),
        ("frontend", "FrontendAgent"),
        ("database", "DatabaseAgent"),
        ("devops", "DevOpsAgent"),
        ("qa", "QAAgent"),
    ]
    
    results = {}
    
    for module_name, class_name in agents_to_test:
        print(f"Running {class_name}...")
        try:
            module = __import__(f"app.agents.{module_name}.{module_name}_agent", fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent = agent_class()
            
            # Find the right method
            methods = ['analyze_project', 'plan_project', 'design_architecture', 
                      'develop_frontend', 'design_database', 'deploy_project',
                      'customer_support', 'run']
            
            result = None
            for method in methods:
                if hasattr(agent, method):
                    result = await getattr(agent, method)(task)
                    break
            
            if result:
                length = len(str(result))
                print(f"  ✅ {class_name}: {length} chars")
                results[class_name] = length
            else:
                print(f"  ⚠️ {class_name}: No output")
        except Exception as e:
            print(f"  ❌ {class_name}: {str(e)[:80]}")
        print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, length in results.items():
        print(f"✅ {name}: {length} chars")

asyncio.run(test_agents())
