from pathlib import Path
import os


class ContextManager:

    """
    Provides controlled project context.

    IMPORTANT:
    project_context.md is the authoritative project context.

    Other workspace files are not automatically treated as
    authoritative project facts.
    """

    def __init__(self):

        if os.getenv("VERCEL"):
            self.workspace = Path("/tmp/ai-software-company/workspace")
        else:
            self.workspace = Path(__file__).resolve().parents[1] / "workspace"

        self.max_file_size = 5000

        self.authoritative_file = self.workspace / "project_context.md"

    # -----------------------------------------------------
    # AUTHORITATIVE CONTEXT
    # -----------------------------------------------------

    def read_authoritative_context(self) -> str:

        if not self.authoritative_file.exists():
            return "Not provided in current project context."

        try:
            return self.authoritative_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except Exception as exc:
            return f"Unable to read authoritative project context: {exc}"

    # -----------------------------------------------------
    # CONTROLLED CONTEXT
    # -----------------------------------------------------

    def build_context(self):

        authoritative = self.read_authoritative_context()

        return (
            "========== AUTHORITATIVE PROJECT CONTEXT ==========\n\n"
            + authoritative
            + "\n\n"
            "===================================================\n"
            "IMPORTANT: Other workspace files are not authoritative "
            "project facts unless explicitly confirmed.\n"
        )

    # -----------------------------------------------------
    # FILE LISTING
    # -----------------------------------------------------

    def list_files(self):

        files = []

        if not self.workspace.exists():
            return files

        for file in self.workspace.rglob("*"):

            if file.is_file():
                files.append(str(file))

        return sorted(files)

    # -----------------------------------------------------
    # SAFE FILE READING
    # -----------------------------------------------------

    def read_file(self, relative_path):

        file = self.workspace / relative_path

        if not file.exists():
            return ""

        return file.read_text(
            encoding="utf-8",
            errors="ignore",
        )


context_manager = ContextManager()
