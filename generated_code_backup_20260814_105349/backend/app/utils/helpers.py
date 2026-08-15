from fastapi.responses import JSONResponse
from app.core.config import settings

class Helpers:
    @staticmethod
    def generate_secret():
        return str(settings.SECRET_KEY)

    @staticmethod
    def generate_access_token(user):
        # Simulate generating a JWT token
        expiration = int(settings.TOKEN_EXPIRY)
        payload = {
            "user_id": user.user_id,
            "exp": expiration
        }
        import json
        token = json.dumps(payload, ensure_ascii=False)
        expires = expiration  # Assuming 'expires' is defined somewhere in the context
        return token, expires

    @staticmethod
    def generate_auth_header(token):
        return {"Authorization": f"Bearer {token}"}