from pathlib import Path


class FileWriter:

    def __init__(self):

        self.root = Path("generated_code")

        self.root.mkdir(
            exist_ok=True
        )

    def write(self, path: str, content: str):

        file = self.root / path

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file.write_text(
            content,
            encoding="utf-8"
        )

        print(f"âœ… Generated: {file}")
