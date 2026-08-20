import json

from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory


class FilePlannerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "file_planner",
            "Technical File Architecture Planner"
        )

    async def run(self, task: str):

        print("File Planner Started")

        blueprint = {

            "backend": [
                "backend/app/main.py",
                "backend/app/core/config.py",
                "backend/app/core/security.py",
                "backend/app/database.py",

                "backend/app/models/user.py",
                "backend/app/models/project.py",

                "backend/app/schemas/user.py",
                "backend/app/schemas/project.py",

                "backend/app/api/routes/auth.py",
                "backend/app/api/routes/users.py",
                "backend/app/api/routes/projects.py",

                "backend/app/services/auth_service.py",
                "backend/app/services/user_service.py",
                "backend/app/services/project_service.py",

                "backend/app/utils/helpers.py",

                "backend/requirements.txt"
            ],

            "frontend": [
                "frontend/src/main.tsx",
                "frontend/src/App.tsx",

                "frontend/src/pages/Home.tsx",
                "frontend/src/pages/Login.tsx",

                "frontend/src/components/Navbar.tsx",
                "frontend/src/components/Footer.tsx"
            ],

            "database": [
                "database/schema.sql"
            ]
        }

        # Save structured blueprint to shared project memory.
        memory.save(
            "file_planner",
            json.dumps(blueprint, indent=4)
        )

        # Save a human-readable planning document.
        self.project_memory.write(
            "planning/file_list.md",
            json.dumps(blueprint, indent=4)
        )

        print("File blueprint saved")

        return blueprint
