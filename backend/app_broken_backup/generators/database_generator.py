from app.generators.base_generator import BaseGenerator


class DatabaseGenerator(BaseGenerator):

    def generate(self, sql: str):

        path = "database/schema.sql"

        self.save(path, sql)

        return self.create_result(path, sql)