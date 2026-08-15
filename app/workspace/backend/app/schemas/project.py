from typing import List, Optional

class ProjectSchema:
    class Backend:
        def __init__(self):
            self.database = "SQL"
            self.api = "RESTful"
            self.frontend = "Web"

    class Frontend:
        def __init__(self):
            self.template_engine = "Django"
            self.database_driver = "MySQL"
            self.database_url = "db:localhost:3306/customers"
            self.security_backend = "JWT"

    class QA:
        def __init__(self):
            self.qa_framework = "TestNG"
            self.test_cases = ["Login Tests", "User Management Tests"]
            self.supporting_files = [
                "tests/login_test.py",
                "models/user.py",
                "controllers/api.py"
            ]
            self.result_files = [
                "logs/login_results.log",
                "logs/user_management_results.log"
            ]

    class Security:
        def __init__(self):
            self.authentication_backend = "OAuth2.0"
            self.authorization_credential_store = "Passport"