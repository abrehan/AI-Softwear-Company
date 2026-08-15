from pathlib import Path


class FileTool:

    async def read(self, path: str):

        file = Path(path)

        if not file.exists():
            return ""

        return file.read_text(
            encoding="utf-8"
        )

    async def write(self, path: str, content: str):

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file.write_text(
            content,
            encoding="utf-8"
        )

        return str(file)


tools = FileTool()