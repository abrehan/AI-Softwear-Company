from fastapi import Depends, HTTPException, status
from database.models.user import User
import bcrypt

async def create_user(user: User, db: Session) -> User:
    """
    Create a new user in the database.

    Args:
        user (User): The new user object to be created.

    Returns:
        User: A new user object.
    """
    # Check if the email already exists
    existing_user = await db.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.BAD_REQUEST, detail="Email already exists")

    # Generate a salt and hash the password
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

    # Create a new user object
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    # Add the new user to the database
    await db.add(new_user)
    await db.commit()

    return new_user