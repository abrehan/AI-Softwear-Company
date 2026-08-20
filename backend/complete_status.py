from pathlib import Path
import os

print("=" * 70)
print("🏢 VIRTUAL OFFICE - COMPLETE STATUS")
print("=" * 70)
print()

agents_dir = Path("app/agents")
total = 0
total_size = 0

print("AGENT ROSTER:")
print("-" * 70)

for folder in sorted(agents_dir.iterdir()):
    if folder.is_dir() and folder.name != "__pycache__":
        total += 1
        agent_files = list(folder.glob("*.py"))
        if agent_files:
            total_size += sum(f.stat().st_size for f in agent_files)
            for agent_file in agent_files:
                size = agent_file.stat().st_size
                print(f"  ✅ {folder.name:20} {agent_file.name:20} {size:>8,} bytes")
        else:
            print(f"  ❌ {folder.name:20} {'NO FILES':20}")

print()
print("-" * 70)
print(f"📊 Total Agents: {total}")
print(f"📊 Total Code: {total_size:,} bytes ({total_size/1024:.1f} KB)")
print("=" * 70)

# Check generated outputs
print()
print("📁 GENERATED OUTPUTS:")
print("-" * 70)

output_dirs = [
    "workspace",
    "app/workspace",
    "generated_code"
]

for dir_path in output_dirs:
    path = Path(dir_path)
    if path.exists():
        files = list(path.rglob("*.md")) + list(path.rglob("*.py"))
        print(f"  📁 {dir_path}: {len(files)} files")
        for f in files[:5]:  # Show first 5
            size = f.stat().st_size
            print(f"      📄 {f.name}: {size:,} bytes")
        if len(files) > 5:
            print(f"      ... and {len(files)-5} more")
    else:
        print(f"  ❌ {dir_path}: Not found")

print()
print("=" * 70)
