import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_orchestrator():
    print("=" * 70)
    print("TESTING ORCHESTRATOR (CEO + CTO WORKFLOW)")
    print("=" * 70)
    print()
    
    from app.agents.orchestrator_agent import OrchestratorAgent
    
    orchestrator = OrchestratorAgent()
    
    project_request = """
    Build a multi-tenant hotel booking platform with:
    - Hotel search and booking engine
    - Payment processing with Stripe
    - User authentication and profiles
    - Admin dashboard
    - Supplier API integration (HotelBeds, Expedia)
    - Multi-currency support
    - Mobile-responsive React frontend
    - ASP.NET Core 8.0 backend
    - SQL Server database
    """
    
    try:
        result = await orchestrator.execute(project_request)
        
        print("\n" + "=" * 70)
        print("✅ ORCHESTRATION SUCCESSFUL!")
        print("=" * 70)
        print()
        print(f"CEO Output length: {len(result['ceo_output'])} characters")
        print(f"CTO Output length: {len(result['cto_output'])} characters")
        print(f"Combined plan saved to: workspace/project/complete_plan.md")
        print()
        
        # Show preview
        print("Preview of combined plan:")
        print("-" * 70)
        print(result['combined'][:500] + "...")
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_orchestrator())
    sys.exit(0 if success else 1)
