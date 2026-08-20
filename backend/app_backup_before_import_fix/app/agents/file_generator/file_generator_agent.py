from pathlib import Path

from backend.app.agents.base_agent import BaseAgent


class FileGeneratorAgent(BaseAgent):

    async def run(self, task):

        manifest = Path(
            "app/workspace/plans/file_manifest.txt"
        )

        files = manifest.read_text().splitlines()

        for file in files:

            print(f"Generating {file}")

            prompt = f"""
Generate ONLY this file.

{file}

Return only code.

No explanation.
"""

            code = await self.think(prompt)

            self.save_file(
                "",
                file,
                code
            )

        return "Completed"
