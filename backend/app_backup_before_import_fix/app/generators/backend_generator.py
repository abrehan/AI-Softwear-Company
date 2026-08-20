from backend.app.generators.code_generator import CodeGenerator


class BackendGenerator:

    def __init__(self):

        self.generator = CodeGenerator()

    def generate(self, response: str):

        return self.generator.generate(response)
