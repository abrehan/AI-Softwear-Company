from pathlib import Path


class ProjectMemory:

    def __init__(self):
        self.workspace = Path("app/workspace")

    def read(self, relative_path):
        file = self.workspace / relative_path

        if file.exists():
            return file.read_text(encoding="utf-8")

        return ""

    def write(self, relative_path, text):
        file = self.workspace / relative_path

        file.parent.mkdir(parents=True, exist_ok=True)

        file.write_text(text, encoding="utf-8")

        return str(file)

    def exists(self, relative_path):
        return (self.workspace / relative_path).exists()

    def list_files(self):
        return [
            str(f.relative_to(self.workspace))
            for f in self.workspace.rglob("*")
            if f.is_file()
        ]


project_memory = ProjectMemory()

# Backward compatibility
memory = project_memory