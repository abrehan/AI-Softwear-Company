from pathlib import Path
from typing import List


class ProjectMemory:

    def __init__(self):
        # Base workspace
        self.workspace = Path("app/workspace")
        self.workspace.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # RAW FILE OPERATIONS
    # =====================================================

    def read(self, relative_path: str) -> str:
        file = self.workspace / relative_path

        if not file.exists():
            return ""

        return file.read_text(
            encoding="utf-8"
        )

    def write(self, relative_path: str, text: str) -> str:

        file = self.workspace / relative_path

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file.write_text(
            text,
            encoding="utf-8"
        )

        print(f"💾 Saved: {file}")

        return str(file)

    def append(self, relative_path: str, text: str):

        file = self.workspace / relative_path

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(file, "a", encoding="utf-8") as f:
            f.write(text)

    def delete(self, relative_path: str):

        file = self.workspace / relative_path

        if file.exists():
            file.unlink()

    # =====================================================
    # KEY / VALUE MEMORY
    # =====================================================

    def set(self, key: str, value: str):
        return self.write(f"{key}.md", value)

    def save(self, key: str, value: str):
        return self.set(key, value)

    def get(self, key: str):
        return self.read(f"{key}.md")

    # =====================================================
    # UTILITIES
    # =====================================================

    def exists(self, relative_path: str):

        return (self.workspace / relative_path).exists()

    def list_files(self) -> List[str]:

        return [

            str(file.relative_to(self.workspace))

            for file in self.workspace.rglob("*")

            if file.is_file()

        ]

    def clear(self):

        for file in self.workspace.rglob("*"):

            if file.is_file():
                file.unlink()


project_memory = ProjectMemory()

# backward compatibility
memory = project_memory