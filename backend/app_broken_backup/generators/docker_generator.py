from app.generators.base_generator import BaseGenerator


class DockerGenerator(BaseGenerator):

    def generate(self, dockerfile: str):

        path = "deployment/Dockerfile"

        self.save(path, dockerfile)

        return self.create_result(path, dockerfile)