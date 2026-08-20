from pathlib import Path
import os


class ContextManager:

    """
    Controlled project-context loader.

    IMPORTANT:
    project_context.md is authoritative.
    Other workspace files are treated as supporting/untrusted context.
    """

    def __init__(self):
        if os.getenv("VERCEL"):
            self.workspace = Path("/tmp/ai-software-company/workspace")
        else:
            self.workspace = (
                Path(__file__).resolve().parents[1] / "workspace"
            )

        self.authoritative_file = self.workspace / "project_context.md"
        self.policy_file = self.workspace / "WORKSPACE_POLICY.md"

        self.max_file_size = 5000

    # --------------------------------------------------------
    # AUTHORITATIVE CONTEXT
    # --------------------------------------------------------

    def load_authoritative_context(self) -> str:

        if not self.authoritative_file.exists():
            return "Not provided in current project context."

        try:
            text = self.authoritative_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            if len(text) > self.max_file_size:
                text = text[:self.max_file_size]
                text += "\n\n...[TRUNCATED]..."

            return text

        except Exception as exc:
            return (
                "Not provided in current project context.\n"
                f"Context read error: {exc}"
            )

    # --------------------------------------------------------
    # CONTROLLED AGENT CONTEXT
    # --------------------------------------------------------

    def build_authoritative_context(self) -> str:

        authoritative = self.load_authoritative_context()

        return f"""
===================================================
AUTHORITATIVE PROJECT CONTEXT
===================================================

{authoritative}

===================================================
AUTHORITY RULE
===================================================

Only the project_context.md content above is authoritative.

Agent outputs, recommendations, generated files, plans,
architecture documents, and generated code are not authoritative
project facts unless explicitly promoted by an approved process.
"""

    # --------------------------------------------------------
    # SUPPORTING CONTEXT
    # --------------------------------------------------------

    def read_supporting_file(self, relative_path: str) -> str:

        file = self.workspace / relative_path

        if not file.exists() or not file.is_file():
            return ""

        try:
            text = file.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            if len(text) > self.max_file_size:
                text = text[:self.max_file_size]
                text += "\n\n...[TRUNCATED]..."

            return text

        except Exception:
            return ""

    def build_agent_context(
        self,
        include_ceo=True,
        include_pm=True,
        include_cto=False,
    ) -> str:

        sections = []

        sections.append(
            self.build_authoritative_context()
        )

        if include_ceo:
            ceo = self.read_supporting_file("ceo.md")
            if ceo:
                sections.append(
                    "\n===================================================\n"
                    "CEO DECISION OUTPUT — NOT AUTHORITATIVE\n"
                    "===================================================\n"
                    f"{ceo}"
                )

        if include_pm:
            pm = self.read_supporting_file("pm.md")
            if pm:
                sections.append(
                    "\n===================================================\n"
                    "PM DECISION OUTPUT — NOT AUTHORITATIVE\n"
                    "===================================================\n"
                    f"{pm}"
                )

        if include_cto:
            cto = self.read_supporting_file("cto.md")
            if cto:
                sections.append(
                    "\n===================================================\n"
                    "CTO DECISION OUTPUT — NOT AUTHORITATIVE\n"
                    "===================================================\n"
                    f"{cto}"
                )

        return "\n".join(sections)

    # --------------------------------------------------------
    # FILE UTILITIES
    # --------------------------------------------------------

    def list_files(self):

        if not self.workspace.exists():
            return []

        return sorted(
            str(file.relative_to(self.workspace))
            for file in self.workspace.rglob("*")
            if file.is_file()
        )

    def read_file(self, relative_path):

        return self.read_supporting_file(relative_path)


context_manager = ContextManager()
