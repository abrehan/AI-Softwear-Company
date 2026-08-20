import re


class FileParser:

    @staticmethod
    def parse(response: str):

        files = []

        # Format 1:
        # ===FILE: path===
        pattern1 = r"===FILE:\s*(.*?)===\n(.*?)(?=(?:===FILE:)|(?:===END===)|\Z)"

        matches = re.findall(
            pattern1,
            response,
            re.DOTALL
        )

        if matches:

            for path, content in matches:

                files.append(
                    {
                        "path": path.strip(),
                        "content": content.strip()
                    }
                )

            return files

        # -------------------------------------------------
        # Format 2:
        # ```python
        # # backend/app/main.py
        # code...
        # ```
        # -------------------------------------------------

        pattern2 = r"```(?:python)?\n#\s*(.*?)\n(.*?)```"

        matches = re.findall(
            pattern2,
            response,
            re.DOTALL
        )

        for path, content in matches:

            files.append(
                {
                    "path": path.strip(),
                    "content": content.strip()
                }
            )

        return files
