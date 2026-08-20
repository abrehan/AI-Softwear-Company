# backend/app/core/config.py

class Config:
    """Configuration class for the application."""
    DATABASE_URL = "mongodb://localhost:27017/virtual-office"
    JWT_SECRET_KEY = "your_secret_key_here"
    API_TITLE = "AI Software Company Virtual Office"
    API_DESCRIPTION = "The AI Software Company virtual office provides a scalable and secure environment for developing and launching AI-powered solutions."
