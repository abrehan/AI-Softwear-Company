import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# All 30 agents
ALL_AGENTS = [
    ("ai_engineer", "AIEngineerAgent"),
    ("backend", "BackendAgent"),
    ("business_analyst", "BusinessAnalystAgent"),
    ("ceo", "CEOAgent"),
    ("code_reviewer", "CodeReviewerAgent"),
    ("cto", "CTOAgent"),
    ("customer_support", "CustomerSupportAgent"),
    ("database", "DatabaseAgent"),
    ("devops", "DevOpsAgent"),
    ("devsecops", "DevSecOpsAgent"),
    ("file_generator", "FileGeneratorAgent"),
    ("file_planner", "FilePlannerAgent"),
    ("finance", "FinanceAgent"),
    ("frontend", "FrontendAgent"),
    ("git_manager", "GitManagerAgent"),
    ("hr", "HRAgent"),
    ("legal", "LegalAgent"),
    ("marketing", "MarketingAgent"),
    ("ml_engineer", "MLEngineerAgent"),
    ("pm", "PMAgent"),
    ("project_manager", "ProjectManagerAgent"),
    ("prompt_engineer", "PromptEngineerAgent"),
    ("qa", "QAAgent"),
    ("recruiter", "RecruiterAgent"),
    ("sales", "SalesAgent"),
    ("security", "SecurityAgent"),
    ("seo", "SEOAgent"),
    ("social_media", "SocialMediaAgent"),
    ("technical_writer", "TechnicalWriterAgent"),
    ("uiux", "UIUXAgent"),
]

async def run_agent(module_name, class_name, test_task):
    try:
        module = __import__(f"app.agents.{module_name}.{module_name}_agent", fromlist=[class_name])
        agent_class = getattr(module, class_name)
        agent = agent_class()
        
        # Try different methods
        for method in ['analyze_project', 'plan_project', 'design_architecture', 
                       'generate_code', 'develop_frontend', 'design_database',
                       'deploy_project', 'devsecops_strategy', 'customer_support',
                       'run']:
            if hasattr(agent, method):
                result = await getattr(agent, method)(test_task)
                return len(result) if result else 0
        return 0
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return -1

async def run_all():
    print("=" * 70)
    print("🏢 RUNNING ALL 30 VIRTUAL OFFICE AGENTS")
    print("=" * 70)
    print()
    
    test_task = "Build a multi-tenant hotel booking platform with payment processing and user authentication."
    
    results = {}
    total = len(ALL_AGENTS)
    
    for i, (module, class_name) in enumerate(ALL_AGENTS, 1):
        print(f"[{i}/{total}] Running {class_name}...")
        length = await run_agent(module, class_name, test_task)
        
        if length > 0:
            print(f"  ✅ {class_name}: {length} chars")
            results[class_name] = length
        elif length == 0:
            print(f"  ⚠️ {class_name}: No output")
            results[class_name] = 0
        else:
            print(f"  ❌ {class_name}: Failed")
            results[class_name] = -1
        print()
    
    print("=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    
    working = sum(1 for v in results.values() if v > 0)
    failed = sum(1 for v in results.values() if v < 0)
    empty = sum(1 for v in results.values() if v == 0)
    
    print(f"✅ Working: {working}")
    print(f"⚠️ Empty output: {empty}")
    print(f"❌ Failed: {failed}")
    print()
    
    if working > 0:
        print("Working agents:")
        for name, length in results.items():
            if length > 0:
                print(f"  ✅ {name}: {length} chars")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_all())
