from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.core.security import authenticate_user, create_access_token, get_current_user

class AuthService:
    def authenticate(self, username: str, password: str) -> UserRead:
        user = self.get_user(username)
        if not user or not authenticate_user(user, password):
            return None
        access_token = create_access_token(data={"sub": user.username})
        return UserRead(**user.dict(), access_token=access_token)

    def get_user(self, username: str) -> User:
        with SessionLocal() as db:
            return db.query(User).filter(User.username == username).first()

    def update_user(self, user_id: int, user_update: UserUpdate) -> UserRead:
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            user = user.update(user_update.dict(exclude_unset=True))
            db.commit()
            db.refresh(user)
            return UserRead(**user.dict())

    def delete_user(self, user_id: int) -> bool:
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True