from pathlib import Path
from typing import List
import os
import re


class ProjectMemory:

    """
    Agent decision memory.

    IMPORTANT:
    This memory is NOT authoritative project state.
    """

    def __init__(self):

        if os.getenv("VERCEL"):
            self.workspace = Path(
                "/tmp/ai-software-company/workspace"
            )
        else:
            self.workspace = (
                Path(__file__).resolve().parents[1] / "workspace"
            )

        self.workspace.mkdir(
            parents=True,
            exist_ok=True
        )

    def _safe_name(self, value: str) -> str:

        value = str(value).strip()

        value = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]',
            "_",
            value
        )

        value = re.sub(
            r"\s+",
            "_",
            value
        )

        value = re.sub(
            r"_+",
            "_",
            value
        )

        value = value.rstrip(". ")

        if not value:
            value = "memory"

        return value[:120]

    def _safe_file(self, relative_path: str) -> Path:

        relative_path = str(relative_path)

        parts = Path(relative_path).parts

        safe_parts = [
            self._safe_name(part)
            for part in parts
            if part not in ("", ".", "..")
        ]

        return self.workspace.joinpath(*safe_parts)

    def read(self, relative_path: str) -> str:

        file = self._safe_file(relative_path)

        if not file.exists():
            return ""

        return file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    def write(self, relative_path: str, text: str) -> str:

        file = self._safe_file(relative_path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file.write_text(
            str(text),
            encoding="utf-8"
        )

        print(f"Saved: {file}")

        return str(file)

    def append(self, relative_path: str, text: str):

        file = self._safe_file(relative_path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            file,
            "a",
            encoding="utf-8"
        ) as handle:
            handle.write(str(text))

    def delete(self, relative_path: str):

        file = self._safe_file(relative_path)

        if file.exists():
            file.unlink()

    def set(self, key: str, value: str):

        safe_key = self._safe_name(key)

        return self.write(
            f"{safe_key}.md",
            value
        )

    def save(self, key: str, value: str):

        return self.set(key, value)

    def get(self, key: str):

        safe_key = self._safe_name(key)

        return self.read(
            f"{safe_key}.md"
        )

    def exists(self, relative_path: str):

        return self._safe_file(
            relative_path
        ).exists()

    def list_files(self) -> List[str]:

        return sorted(
            str(file.relative_to(self.workspace))
            for file in self.workspace.rglob("*")
            if file.is_file()
        )

    def clear(self):

        for file in self.workspace.rglob("*"):

            if file.is_file():
                file.unlink()


project_memory = ProjectMemory()

memory = project_memory
