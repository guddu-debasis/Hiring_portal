import os
from dotenv import load_dotenv

# Ensure this is at the very top
load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Hiring Automator"
    
    # Use defaults to prevent NoneType errors
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB", "hiring_db")
    
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "7d8f9e0a1b2c3d4e5f6g7h8i9j0k1l2m")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    
    # Robust integer conversion
    _raw_expiry = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(_raw_expiry) if _raw_expiry.isdigit() else 60

settings = Settings()