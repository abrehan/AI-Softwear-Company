from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class BackendModule(ABC):
    @abstractmethod
    def login(self) -> bool:
        """Authenticate a user."""
        pass

    @abstractmethod
    def get_database_connection(self) -> str:
        """Get the database connection string."""
        pass

    @abstractmethod
    def create_user(self, username: str, password: str) -> None:
        """Create a new user."""
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user by credentials."""
        pass

    @abstractmethod
    def get_user_details(self, user_id: int) -> Dict[str, str]:
        """Get details about a user by ID."""
        pass

class DatabaseModule(ABC):
    @abstractmethod
    def create_database(self, name: str) -> None:
        """Create a new database."""
        pass

    @abstractmethod
    def select_user_from_database(self, username: str, password: str) -> Dict[str, str]:
        """Select a user from the database by credentials."""
        pass

class ApiModule(ABC):
    @abstractmethod
    def create_api(self, name: str) -> None:
        """Create a new API."""
        pass

    @abstractmethod
    def get_user_endpoint(self, username: str) -> str:
        """Get the endpoint of a user's API."""
        pass

class FrontendModule(ABC):
    @abstractmethod
    def create_frontend(self, name: str) -> None:
        """Create a new frontend."""
        pass

    @abstractmethod
    def get_user_interface_element(self, username: str) -> str:
        """Get the UI element of a user's front-end component."""
        pass

class SecurityModule(ABC):
    @abstractmethod
    def create_security_layer(self, name: str) -> None:
        """Create a new security layer."""
        pass

    @abstractmethod
    def get_security_configuration(self, username: str) -> Dict[str, str]:
        """Get the security configuration of a user's frontend component."""
        pass