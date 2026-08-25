import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_fixed_agents():
    print("=" * 70)
    print("🧪 TESTING FIXED AGENTS")
    print("=" * 70)
    print()
    
    test_task = "Build a multi-tenant hotel booking platform"
    
    agents_to_test = [
        ("app.agents.architect", "ArchitectAgent"),
        ("app.agents.documentation", "DocumentationAgent"),
        ("app.agents.file_generator", "FileGeneratorAgent"),
    ]
    
    results = {}
    
    for module_path, class_name in agents_to_test:
        print(f"Testing {class_name}...")
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent = agent_class()
            
            # Find the right method
            methods = ['design_architecture', 'create_documentation', 'generate_files', 'run']
            
            result = None
            for method in methods:
                if hasattr(agent, method):
                    result = await getattr(agent, method)(test_task)
                    break
            
            if result:
                length = len(str(result))
                print(f"  ✅ {class_name}: {length} chars")
                results[class_name] = length
            else:
                print(f"  ⚠️ {class_name}: No output")
                results[class_name] = 0
        except Exception as e:
            print(f"  ❌ {class_name}: {str(e)[:80]}")
            results[class_name] = -1
        print()
    
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    for name, length in results.items():
        if length > 0:
            print(f"✅ {name}: {length} chars")
        elif length == 0:
            print(f"⚠️ {name}: No output")
        else:
            print(f"❌ {name}: Failed")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_fixed_agents())
