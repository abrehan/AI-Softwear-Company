from pathlib import Path

print("=" * 70)
print("🏢 VIRTUAL OFFICE - FULL STATUS")
print("=" * 70)
print()

agents_dir = Path("app/agents")
agent_folders = [d for d in agents_dir.iterdir() if d.is_dir()]

print(f"Total Agents: {len(agent_folders)}")
print()

for folder in sorted(agent_folders):
    agent_file = folder / f"{folder.name}_agent.py"
    if agent_file.exists():
        size = agent_file.stat().st_size
        print(f"✅ {folder.name}: {size} bytes")
    else:
        py_files = list(folder.glob("*.py"))
        if py_files:
            for py_file in py_files:
                size = py_file.stat().st_size
                print(f"✅ {folder.name}: {py_file.name} ({size} bytes)")
        else:
            print(f"❌ {folder.name}: No Python files")

print()
print("=" * 70)
