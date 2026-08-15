from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = Column(User)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner.id if self.owner else None
        }

class ProjectTask(Base):
    __tablename__ = "project_tasks"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum('Pending', 'Completed'), default='Pending')
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class ProjectUser(Base):
    __tablename__ = "project_users"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum('Active', 'Inactive'), default='Active')
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    permission_type = Column(Enum('Read', 'Write'), default='Read')
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    permissions = relationship("Permission", back_populates="role")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class UserService:
    def __init__(self):
        self.engine = create_engine('sqlite:///user_management.db')
        Base.metadata.create_all(self.engine)
    
    def get_user_by_id(self, user_id: int) -> User:
        return User.query.filter_by(id=user_id).first()
    
    def create_user(self, username: str, email: str) -> User:
        new_user = User(username=username, email=email)
        self.session.add(new_user)
        self.session.commit()
        return new_user
    
    def get_projects(self, user_id: int) -> List[Project]:
        project_query = Project.query
        if user_id:
            project_query = project_query.filter_by(owner_id=user_id)
        
        projects = project_query.all()
        return projects

    def create_project(self, name: str, description: str, owner_id: int) -> Project:
        new_project = Project(name=name, description=description, owner=owner_id)
        self.session.add(new_project)
        self.session.commit()
        return new_project
    
    def get_tasks(self, project_id: int) -> List[ProjectTask]:
        task_query = ProjectTask.query
        if project_id:
            task_query = task_query.filter_by(project_id=project_id)
        
        tasks = task_query.all()
        return tasks

    def create_task(self, title: str, description: str, project_id: int, status: str) -> ProjectTask:
        new_task = ProjectTask(title=title, description=description, project_id=project_id, status=status)
        self.session.add(new_task)
        self.session.commit()
        return new_task
    
    def create_permission(self, project_id: int, user_id: int, permission_type: str) -> Permission:
        new_permission = Permission(project_id=project_id, user_id=user_id, permission_type=permission_type)
        self.session.add(new_permission)
        self.session.commit()
        return new_permission

    def get_role(self, role_name: str) -> Role:
        role_query = Role.query.filter_by(name=role_name)
        return role_query.first()

# Example usage
if __name__ == "__main__":
    # Assuming a database connection is established in the following way
    session = UserService()
    
    # Create a user
    user = session.create_user(username="john_doe", email="user@example.com")
    
    # Get projects
    projects = session.get_projects(user_id=1)
    
    for project in projects:
        print(project.to_dict())
```

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "user@example.com"
}