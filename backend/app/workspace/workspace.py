from pathlib import Path
import os


class Workspace:

    def __init__(self):
        # Vercel filesystem is read-only except /tmp.
        # Local development uses backend/app/workspace.
        if os.getenv("VERCEL"):
            self.root = Path("/tmp/ai-software-company/workspace")
        else:
            self.root = Path(__file__).resolve().parent

        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, content: str):
        file_path = self.root / path

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        print(f"Saved: {file_path}")

        return file_path

    def read(self, path: str):
        file_path = self.root / path

        if not file_path.exists():
            return ""

        return file_path.read_text(
            encoding="utf-8"
        )

    def exists(self, path: str):
        return (self.root / path).exists()

    def delete(self, path: str):
        file_path = self.root / path

        if file_path.exists():
            file_path.unlink()

    def list_files(self):
        return [
            str(file.relative_to(self.root))
            for file in self.root.rglob("*")
            if file.is_file()
        ]


workspace = Workspace()
