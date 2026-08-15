from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

auth_route = router.get("/login")
async def login_user(
    auth_code: str,
    db: Session = Depends(get_db)
) -> dict:
    # Find user based on the provided code
    user = await db.query(User).filter_by(auth_code=auth_code).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication code")

    return {"message": "Login successful", "user_id": user.id}