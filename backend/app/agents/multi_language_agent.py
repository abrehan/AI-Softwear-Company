# app/agents/multi_language_agent.py
"""
Base agent with multi-language support
"""

from app.config.languages import LANGUAGE_CONFIG, MODEL_RECOMMENDATIONS
from app.agents.base_agent import BaseAgent

class MultiLanguageAgent(BaseAgent):
    """Base agent with language awareness"""
    
    def __init__(self, name, role, languages=None):
        super().__init__(name, role)
        self.supported_languages = languages or []
        self.default_language = "python"
    
    def get_model_for_language(self, language: str) -> str:
        """Get recommended model for specific language"""
        return MODEL_RECOMMENDATIONS.get(language, "codellama:7b")
    
    def get_language_config(self, language: str) -> dict:
        """Get configuration for specific language"""
        return LANGUAGE_CONFIG.get(language, {})
    
    def generate_language_prompt(self, task: str, language: str) -> str:
        """Generate prompt with language-specific context"""
        config = self.get_language_config(language)
        extensions = ", ".join(config.get("extensions", []))
        frameworks = ", ".join(config.get("framework", []))
        
        return f"""
Task: {task}

Language: {language}
File extensions: {extensions}
Recommended frameworks: {frameworks}
Package manager: {config.get('package_manager', 'N/A')}
Testing: {', '.join(config.get('testing', ['N/A']))}
Linting: {', '.join(config.get('linting', ['N/A']))}

Generate production-ready code in {language} with proper error handling,
testing, and documentation. Follow {language} best practices and
conventions.
"""
