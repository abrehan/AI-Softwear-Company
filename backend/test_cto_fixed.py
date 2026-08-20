# test_cto_fixed.py
import asyncio
import sys
from pathlib import Path

# Add the backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_cto():
    print("Testing CTOAgent with newline fix...")
    print("=" * 70)
    
    from app.agents.cto.cto_agent import CTOAgent
    
    agent = CTOAgent()
    
    # Simple test task
    task = "Design the architecture for a multi-tenant hotel booking platform"
    
    try:
        result = await agent.design_architecture(task)
        print("\n✅ CTO Agent completed successfully!")
        print("=" * 70)
        print("Result summary:")
        print("-" * 70)
        print(result[:1000] + "...")
        print("=" * 70)
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cto())
    sys.exit(0 if success else 1)
