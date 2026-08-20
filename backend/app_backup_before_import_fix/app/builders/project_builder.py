from pathlib import Path


class ProjectBuilder:

    def __init__(self):

        self.root = Path("generated_projects")

    def create_project(self, project_name: str):

        project = self.root / project_name

        folders = [

            "backend",

            "frontend",

            "database",

            "docker",

            "docs",

            "tests",

            "scripts",

            ".github/workflows",

            "backend/app",

            "backend/app/api",

            "backend/app/models",

            "backend/app/services",

            "backend/app/routes",

            "frontend/src",

            "frontend/src/pages",

            "frontend/src/components",

            "frontend/src/hooks",

            "frontend/public",

            "database/migrations"

        ]

        for folder in folders:

            (project / folder).mkdir(
                parents=True,
                exist_ok=True
            )

        return project
