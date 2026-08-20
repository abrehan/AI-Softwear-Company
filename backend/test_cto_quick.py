# test_cto_quick.py
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test():
    print("Testing CTOAgent with explicit prompt...")
    print("=" * 70)
    
    from app.agents.cto.cto_agent import CTOAgent
    
    agent = CTOAgent()
    task = "Design the architecture for a multi-tenant hotel booking platform"
    
    try:
        result = await agent.design_architecture(task)
        print("\n✅ SUCCESS! CTO generated complete architecture.")
        print("\nChecking sections...")
        
        required = [
            "# System Architecture",
            "## Project Overview",
            "## Confirmed Current Architecture",
            "## Architecture Gaps",
            "## Recommended Technology Architecture",
            "## Orchestration Architecture",
            "## Context Architecture",
            "## Agent Responsibility Boundaries",
            "## Testing Strategy",
            "## Logging",
            "## Risks",
            "## Next Implementation Sequence",
            "## Recommendations"
        ]
        
        found = []
        missing = []
        for section in required:
            if section.lower() in result.lower():
                found.append(section)
            else:
                missing.append(section)
        
        print(f"Found sections: {len(found)}/{len(required)}")
        if missing:
            print(f"Missing: {missing}")
        else:
            print("✅ All sections found!")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
