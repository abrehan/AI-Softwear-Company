from typing import List, Dict, Optional

# Sample User model from backend/schema.sql
class UserModel:
    id: int = 0
    username: str
    email: str
    password: str
    status: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @classmethod
    def create(cls, username: str, email: str, password: str) -> UserModel:
        user = UserModel(username=username, email=email, password=password)
        return user

    @classmethod
    def find_by_id(cls, id: int) -> Optional[UserModel]:
        return cls.objects.get(id=id)

    @classmethod
    def update_status(cls, id: int, status: bool) -> UserModel:
        user = cls.find_by_id(id)
        if user:
            user.status = status
            user.save()
        return user

    @classmethod
    def delete_user(cls, id: int) -> None:
        user = cls.find_by_id(id)
        if user:
            user.delete()