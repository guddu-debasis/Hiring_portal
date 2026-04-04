import os
from dotenv import load_dotenv

# Ensure this is at the very top
load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Hiring Automator"
    
    # --- 1. MySQL SMART LOGIC ---
    # In Render/TiDB, you will set 'DATABASE_URL' as one long string.
    # Locally, you can keep using your individual MYSQL_ variables.
    _DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Local MySQL Fallbacks (Used only if DATABASE_URL is missing)
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB", "hiring_db")
    
    @property
    def DATABASE_URL(self):
        # If the Cloud string exists, use it exactly as provided.
        if self._DATABASE_URL:
            return self._DATABASE_URL
        
        # Otherwise, build it for your local Windows MySQL.
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
    # --- 2. AI & SECURITY ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "7d8f9e0a1b2c3d4e5f6g7h8i9j0k1l2m")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    
    # Robust integer conversion for token expiry
    _raw_expiry = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(_raw_expiry) if _raw_expiry.isdigit() else 60

settings = Settings()