from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# --- SSL CONFIGURATION FOR CLOUD ---
# TiDB Cloud and other managed MySQL services require SSL.
# This path is the standard CA cert location on Render (Linux).
connect_args = {}
if "tidbcloud" in settings.DATABASE_URL or "aivencloud" in settings.DATABASE_URL:
    connect_args = {
        "ssl": {
            "ca": "/etc/ssl/certs/ca-certificates.crt"
        }
    }

# Create the SQLAlchemy engine with SSL arguments
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our classes to inherit from
Base = declarative_base()

# Dependency to get the DB session in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()