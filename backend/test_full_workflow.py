# test_full_workflow.py
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_full_workflow():
    print("=" * 70)
    print("TESTING FULL WORKFLOW (CEO + PM + CTO)")
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
    - Need to handle 1000+ concurrent users
    """
    
    try:
        result = await orchestrator.execute(project_request)
        
        print("=" * 70)
        print("✅ FULL WORKFLOW SUCCESSFUL!")
        print("=" * 70)
        print()
        print(f"CEO Output: {len(result['ceo_output'])} chars")
        print(f"PM Output: {len(result['pm_output'])} chars")
        print(f"CTO Output: {len(result['cto_output'])} chars")
        print()
        print("Files saved:")
        print("  - workspace/project/complete_plan_with_pm.md")
        print("  - workspace/architecture/system_architecture.md")
        print("  - workspace/project/pm_plan.md")
        print()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_workflow())
    sys.exit(0 if success else 1)
