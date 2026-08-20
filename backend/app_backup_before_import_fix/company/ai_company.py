from app.builders.project_builder import ProjectBuilder


class AICompany:

    def __init__(self):

        self.builder = ProjectBuilder()

    async def build_project(self, project_name: str):

        project = self.builder.create_project(
            project_name
        )

        print(f"📁 Project created: {project}")

        return project