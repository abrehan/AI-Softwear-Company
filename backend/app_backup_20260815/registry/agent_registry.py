from app.agents.ceo.ceo_agent import CEOAgent
from app.agents.project_manager.project_manager_agent import ProjectManagerAgent
from app.agents.cto.cto_agent import CTOAgent

from app.agents.file_planner.file_planner_agent import FilePlannerAgent
from app.agents.backend.backend_agent import BackendAgent
from app.agents.frontend.frontend_agent import FrontendAgent
from app.agents.uiux.uiux_agent import UIUXAgent
from app.agents.database.database_agent import DatabaseAgent
from app.agents.devops.devops_agent import DevOpsAgent
from app.agents.qa.qa_agent import QAAgent
from app.agents.security.security_agent import SecurityAgent
from app.agents.devsecops.devsecops_agent import DevSecOpsAgent
from app.agents.ai_engineer.ai_engineer_agent import AIEngineerAgent
from app.agents.ml_engineer.ml_engineer_agent import MLEngineerAgent
from app.agents.prompt_engineer.prompt_engineer_agent import PromptEngineerAgent
from app.agents.technical_writer.technical_writer_agent import TechnicalWriterAgent
from app.agents.code_reviewer.code_reviewer_agent import CodeReviewerAgent
from app.agents.git_manager.git_manager_agent import GitManagerAgent
from app.agents.business_analyst.business_analyst_agent import BusinessAnalystAgent
from app.agents.marketing.marketing_agent import MarketingAgent
from app.agents.seo.seo_agent import SEOAgent
from app.agents.social_media.social_media_agent import SocialMediaAgent
from app.agents.sales.sales_agent import SalesAgent
from app.agents.customer_support.customer_support_agent import CustomerSupportAgent
from app.agents.finance.finance_agent import FinanceAgent
from app.agents.legal.legal_agent import LegalAgent
from app.agents.hr.hr_agent import HRAgent
from app.agents.recruiter.recruiter_agent import RecruiterAgent


class AgentRegistry:

    def __init__(self):
        self.agents = {
            "ceo": CEOAgent,
            "pm": ProjectManagerAgent,
	    "project_manager": ProjectManagerAgent,
            "cto": CTOAgent,
            "file_planner": FilePlannerAgent,
            "backend": BackendAgent,
            "frontend": FrontendAgent,
            "database": DatabaseAgent,
            "ai": AIEngineerAgent,
            "ml": MLEngineerAgent,
            "prompt": PromptEngineerAgent,
            "security": SecurityAgent,
            "devsecops": DevSecOpsAgent,
            "reviewer": CodeReviewerAgent,
            "qa": QAAgent,
            "writer": TechnicalWriterAgent,
            "git": GitManagerAgent,
            "devops": DevOpsAgent,
            "marketing": MarketingAgent,
            "seo": SEOAgent,
            "social": SocialMediaAgent,
            "sales": SalesAgent,
            "support": CustomerSupportAgent,
            "business": BusinessAnalystAgent,
            "uiux": UIUXAgent,
            "finance": FinanceAgent,
            "legal": LegalAgent,
            "hr": HRAgent,
            "recruiter": RecruiterAgent,
        }

    def get_agent(self, name: str):
        """Return the registered agent CLASS."""
        agent_class = self.agents.get(name)

        if agent_class is None:
            raise ValueError(f"Agent '{name}' is not registered.")

        return agent_class

    def get(self, name: str):
        """Backward-compatible alias for get_agent()."""
        return self.get_agent(name)

    def list(self):
        """Return all registered agent names."""
        return list(self.agents.keys())