class Project:
    id: str = None  # Unique identifier for the project
    name: str = None  # Name of the project
    description: str = None  # Description of the project
    status: str = "Initiated"  # Status of the project
    requirements: dict = {}  # Requirements for the project

    def __repr__(self):
        return f"Project(id={self.id}, name={self.name}, description={self.description}, status={self.status})"