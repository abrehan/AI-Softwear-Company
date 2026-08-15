from app.workspace.workspace import workspace


class BaseGenerator:

    def save(self, path: str, content: str):
        workspace.save(path, content)

    def create_result(self, path: str, content: str):
        return {
            "path": path,
            "content": content
        }