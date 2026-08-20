"""
MASTER ORCHESTRATOR - All 34 Virtual Office Agents
"""

import asyncio
import sys
from pathlib import Path
import importlib

sys.path.insert(0, str(Path(__file__).parent))

class VirtualOffice:
    """Complete Virtual Office with 34 AI Agents."""
    
    def __init__(self):
        self.agents = {}
        self.results = {}
        
        # All 34 agents (excluding __pycache__)
        self.agent_list = [
            ("ai_engineer", "AIEngineerAgent"),
            ("architect", "ArchitectAgent"),
            ("backend", "BackendAgent"),
            ("business_analyst", "BusinessAnalystAgent"),
            ("ceo", "CEOAgent"),
            ("code_reviewer", "CodeReviewerAgent"),
            ("cto", "CTOAgent"),
            ("customer_support", "CustomerSupportAgent"),
            ("database", "DatabaseAgent"),
            ("dev", "DevAgent"),
            ("devops", "DevOpsAgent"),
            ("devsecops", "DevSecOpsAgent"),
            ("documentation", "DocumentationAgent"),
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
    
    def _get_agent_method(self, agent):
        """Find the appropriate method to call on an agent."""
        methods = [
            'analyze_project',
            'plan_project',
            'design_architecture',
            'generate_code',
            'develop_frontend',
            'design_database',
            'deploy_project',
            'devsecops_strategy',
            'customer_support',
            'run'
        ]
        
        for method in methods:
            if hasattr(agent, method):
                return method
        return None
    
    async def load_agent(self, module_name, class_name):
        """Load a single agent by name."""
        try:
            # Try different import patterns
            import_patterns = [
                f"app.agents.{module_name}.{module_name}_agent",
                f"app.agents.{module_name}.agent",
                f"app.agents.{module_name}.main",
            ]
            
            for pattern in import_patterns:
                try:
                    module = importlib.import_module(pattern)
                    if hasattr(module, class_name):
                        agent_class = getattr(module, class_name)
                        return agent_class()
                except ImportError:
                    continue
            
            # Fallback: try to find any Agent class in the module
            try:
                module = importlib.import_module(f"app.agents.{module_name}.{module_name}_agent")
                for attr in dir(module):
                    if attr.endswith("Agent") and attr != "BaseAgent":
                        agent_class = getattr(module, attr)
                        return agent_class()
            except ImportError:
                pass
                
            return None
            
        except Exception as e:
            print(f"  ⚠️ Error loading {class_name}: {e}")
            return None
    
    async def run_all(self, project_task: str):
        """Run all agents with a project task."""
        
        print("=" * 70)
        print("🏢 VIRTUAL OFFICE - ALL 34 AGENTS")
        print("=" * 70)
        print()
        print(f"📋 Project: {project_task[:100]}...")
        print()
        
        total = len(self.agent_list)
        working = 0
        failed = 0
        
        for i, (module_name, class_name) in enumerate(self.agent_list, 1):
            print(f"[{i}/{total}] Loading {class_name}...")
            
            agent = await self.load_agent(module_name, class_name)
            
            if agent is None:
                print(f"  ❌ {class_name}: Failed to load")
                failed += 1
                print()
                continue
            
            method = self._get_agent_method(agent)
            
            if method is None:
                print(f"  ⚠️ {class_name}: No run method found")
                failed += 1
                print()
                continue
            
            try:
                # Run the agent
                result = await getattr(agent, method)(project_task)
                
                if result:
                    length = len(str(result)) if result else 0
                    print(f"  ✅ {class_name}: {length} chars")
                    self.results[class_name] = length
                    working += 1
                else:
                    print(f"  ⚠️ {class_name}: Empty output")
                    self.results[class_name] = 0
                    
            except Exception as e:
                print(f"  ❌ {class_name}: {str(e)[:100]}")
                self.results[class_name] = -1
                failed += 1
            
            print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"✅ Working: {working}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Total: {total}")
        print()
        
        if working > 0:
            print("Working agents:")
            for name, length in sorted(self.results.items()):
                if length > 0:
                    print(f"  ✅ {name}: {length:,} chars")
        
        return self.results
    
    async def run_specific(self, agent_names: list, project_task: str):
        """Run specific agents by name."""
        
        results = {}
        
        for agent_name in agent_names:
            # Find the agent in the list
            found = None
            for module, cls in self.agent_list:
                if cls == agent_name or module == agent_name:
                    found = (module, cls)
                    break
            
            if not found:
                print(f"❌ Agent '{agent_name}' not found")
                continue
            
            module_name, class_name = found
            agent = await self.load_agent(module_name, class_name)
            
            if agent is None:
                print(f"❌ {class_name}: Failed to load")
                continue
            
            method = self._get_agent_method(agent)
            if method is None:
                print(f"❌ {class_name}: No run method")
                continue
            
            try:
                result = await getattr(agent, method)(project_task)
                length = len(str(result)) if result else 0
                print(f"✅ {class_name}: {length} chars")
                results[class_name] = length
            except Exception as e:
                print(f"❌ {class_name}: {e}")
        
        return results


# ============================================================
# COMMAND LINE INTERFACE
# ============================================================

async def main():
    office = VirtualOffice()
    
    print("=" * 70)
    print("🏢 VIRTUAL OFFICE COMMAND CENTER")
    print("=" * 70)
    print()
    print("Commands:")
    print("  all    - Run all 34 agents")
    print("  ceo    - Run CEO only")
    print("  dev    - Run dev team (CEO, PM, CTO, Dev)")
    print("  full   - Run full dev team + ops (CEO, PM, CTO, Dev, Frontend, Backend, Database, DevOps, DevSecOps)")
    print("  list   - List all agents")
    print("  <name> - Run specific agent (e.g., python master.py qa)")
    print()
    
    # Default task
    task = "Build a multi-tenant hotel booking platform with payment processing, user authentication, and supplier API integration."
    
    # Run all by default
    await office.run_all(task)

if __name__ == "__main__":
    asyncio.run(main())
