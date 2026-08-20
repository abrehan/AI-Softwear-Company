from app.agents.ceo.ceo_agent import CEOAgent
from app.agents.cto.cto_agent import CTOAgent
from app.agents.pm.pm_agent import PMAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace

class OrchestratorAgent:
    """Orchestrates the full workflow: CEO -> PM -> CTO."""
    
    def __init__(self):
        self.ceo = CEOAgent()
        self.pm = PMAgent()
        self.cto = CTOAgent()
    
    async def execute(self, project_request: str):
        """Execute full workflow: CEO -> PM -> CTO."""
        
        print("=" * 70)
        print("ORCHESTRATOR: Full Project Workflow")
        print("=" * 70)
        print()
        
        # Step 1: CEO analyzes project
        print("📋 Step 1: CEO Agent analyzing project...")
        ceo_result = await self.ceo.analyze_project(project_request)
        print("✅ CEO analysis complete")
        print()
        
        # Step 2: PM creates plan
        print("📊 Step 2: PM Agent creating project plan...")
        pm_result = await self.pm.plan_project(ceo_result)
        print("✅ PM plan complete")
        print()
        
        # Step 3: CTO designs architecture based on CEO + PM
        print("🏗️  Step 3: CTO Agent designing architecture...")
        architecture_task = f"""
        Based on:
        
        CEO Analysis:
        {ceo_result}
        
        PM Plan:
        {pm_result}
        
        Design the architecture for this project.
        """
        
        cto_result = await self.cto.design_architecture(architecture_task)
        print("✅ CTO architecture design complete")
        print()
        
        # Step 4: Save combined results
        print("💾 Step 4: Saving combined results...")
        
        combined = f"""
# COMPLETE PROJECT PLAN

## ORIGINAL REQUEST
{project_request}

## CEO ANALYSIS
{ceo_result}

## PM PLAN
{pm_result}

## CTO ARCHITECTURE
{cto_result}
"""
        
        workspace.save("project/complete_plan_with_pm.md", combined)
        memory.save("orchestrator_full", combined)
        print("✅ Complete plan saved")
        print()
        
        print("=" * 70)
        print("✅ FULL ORCHESTRATION COMPLETE!")
        print("=" * 70)
        
        return {
            "ceo_output": ceo_result,
            "pm_output": pm_result,
            "cto_output": cto_result,
            "combined": combined
        }
