from pathlib import Path


class FileManifest:

    def __init__(self):
        self.files = []

    def add(self, path: str):
        self.files.append(path)

    def all(self):
        return self.files

    def save(self):

        Path("app/workspace/plans").mkdir(
            parents=True,
            exist_ok=True
        )

        file = Path("app/workspace/plans/file_manifest.txt")

        file.write_text(
            "\n".join(self.files),
            encoding="utf-8"
        )
