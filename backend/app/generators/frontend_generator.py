from app.generators.base_generator import BaseGenerator


class FrontendGenerator(BaseGenerator):

    def generate(self, code: str):

        path = "frontend/src/pages/Home.tsx"

        self.save(path, code)

        return self.create_result(path, code)

