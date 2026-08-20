import os
import sys
from pathlib import Path

print("=" * 70)
print("🔍 SCANNING FOR ALL AGENTS")
print("=" * 70)
print()

agents_dir = Path("app/agents")
if not agents_dir.exists():
    print("❌ Agents directory not found!")
    sys.exit(1)

agents = []
for agent_folder in agents_dir.iterdir():
    if agent_folder.is_dir():
        # Look for agent files
        py_files = list(agent_folder.glob("*_agent.py"))
        if py_files:
            for py_file in py_files:
                # Try to import the agent class
                try:
                    module_name = f"app.agents.{agent_folder.name}.{py_file.stem}"
                    spec = __import__(module_name, fromlist=[''])
                    # Find class that ends with Agent
                    for attr_name in dir(spec):
                        if attr_name.endswith("Agent") and attr_name != "BaseAgent":
                            agent_class = getattr(spec, attr_name)
                            if hasattr(agent_class, '__bases__'):
                                agents.append({
                                    "name": attr_name,
                                    "file": py_file.name,
                                    "folder": agent_folder.name,
                                    "module": module_name
                                })
                except Exception as e:
                    agents.append({
                        "name": f"{agent_folder.name}_Agent",
                        "file": py_file.name,
                        "folder": agent_folder.name,
                        "module": "Error importing"
                    })

print(f"Found {len(agents)} agents:")
print("-" * 70)
for i, agent in enumerate(agents, 1):
    print(f"{i:2}. {agent['name']}")
    print(f"    📁 {agent['folder']}")
    print(f"    📄 {agent['file']}")
    print()

print("=" * 70)
