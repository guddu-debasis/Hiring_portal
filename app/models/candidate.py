from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class JobPost(Base):
    __tablename__ = "job_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    requirements = Column(Text)

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_posts.id"))
    full_name = Column(String(255))
    email = Column(String(255))
    resume_text = Column(Text)
    score = Column(Float)
    # The 'default' ensures new applicants start as 'Pending'
    status = Column(String(50), default="Pending") 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255)) 
    role = Column(String(20)) # "recruiter" or "candidate"