from backend.app.agents.ceo.ceo_agent import CEOAgent
from backend.app.agents.project_manager.project_manager_agent import ProjectManagerAgent
from backend.app.agents.cto.cto_agent import CTOAgent

from backend.app.agents.file_planner.file_planner_agent import FilePlannerAgent
from backend.app.agents.backend.backend_agent import BackendAgent
from backend.app.agents.frontend.frontend_agent import FrontendAgent
from backend.app.agents.uiux.uiux_agent import UIUXAgent
from backend.app.agents.database.database_agent import DatabaseAgent
from backend.app.agents.devops.devops_agent import DevOpsAgent
from backend.app.agents.qa.qa_agent import QAAgent
from backend.app.agents.security.security_agent import SecurityAgent
from backend.app.agents.devsecops.devsecops_agent import DevSecOpsAgent
from backend.app.agents.ai_engineer.ai_engineer_agent import AIEngineerAgent
from backend.app.agents.ml_engineer.ml_engineer_agent import MLEngineerAgent
from backend.app.agents.prompt_engineer.prompt_engineer_agent import PromptEngineerAgent
from backend.app.agents.technical_writer.technical_writer_agent import TechnicalWriterAgent
from backend.app.agents.code_reviewer.code_reviewer_agent import CodeReviewerAgent
from backend.app.agents.git_manager.git_manager_agent import GitManagerAgent
from backend.app.agents.business_analyst.business_analyst_agent import BusinessAnalystAgent
from backend.app.agents.marketing.marketing_agent import MarketingAgent
from backend.app.agents.seo.seo_agent import SEOAgent
from backend.app.agents.social_media.social_media_agent import SocialMediaAgent
from backend.app.agents.sales.sales_agent import SalesAgent
from backend.app.agents.customer_support.customer_support_agent import CustomerSupportAgent
from backend.app.agents.finance.finance_agent import FinanceAgent
from backend.app.agents.legal.legal_agent import LegalAgent
from backend.app.agents.hr.hr_agent import HRAgent
from backend.app.agents.recruiter.recruiter_agent import RecruiterAgent


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
        agent_class = self.agents.get(name)

        if agent_class is None:
            raise ValueError(f"Agent '{name}' is not registered.")

        return agent_class

    def get(self, name: str):
        return self.get_agent(name)

    def list(self):
        return list(self.agents.keys())

    def list_agents(self):
        return self.list()


registry = AgentRegistry()
