from app.generators.parser import FileParser
from app.generators.file_writer import FileWriter


class CodeGenerator:

    def __init__(self):

        self.writer = FileWriter()

    def generate(self, response: str):

        files = FileParser.parse(response)

        for file in files:

            self.writer.write(
                file["path"],
                file["content"]
            )

        return files