from pathlib import Path


class ContextManager:

    def __init__(self):

        self.workspace = Path("app/workspace")

        # Prevent prompts from becoming too large
        self.max_file_size = 5000

    def build_context(self):

        if not self.workspace.exists():
            return "Workspace is empty."

        sections = []

        # Read folders in alphabetical order
        for folder in sorted(self.workspace.iterdir()):

            if not folder.is_dir():
                continue

            sections.append(f"\n========== {folder.name.upper()} ==========\n")

            for file in sorted(folder.glob("*")):

                if not file.is_file():
                    continue

                try:

                    text = file.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )

                    # Limit file size
                    if len(text) > self.max_file_size:
                        text = text[:self.max_file_size]
                        text += "\n\n...[TRUNCATED]..."

                    sections.append(
                        f"""
FILE:
{file.name}

{text}

--------------------------------------------
"""
                    )

                except Exception as e:

                    sections.append(
                        f"{file.name}: ERROR ({e})"
                    )

        if not sections:
            return "No project files found."

        return "\n".join(sections)

    def list_files(self):

        files = []

        if not self.workspace.exists():
            return files

        for file in self.workspace.rglob("*"):

            if file.is_file():
                files.append(str(file))

        return sorted(files)

    def read_file(self, relative_path):

        file = self.workspace / relative_path

        if not file.exists():
            return ""

        return file.read_text(
            encoding="utf-8",
            errors="ignore"
        )


context_manager = ContextManager()