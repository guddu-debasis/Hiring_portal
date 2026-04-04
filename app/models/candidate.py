from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class JobPost(Base):
    __tablename__ = "job_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    requirements = Column(Text)
    
    # Relationship to link jobs and candidates
    candidates = relationship("Candidate", back_populates="job_post")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_posts.id"))
    full_name = Column(String(255))
    email = Column(String(255))
    
    # --- ADD THESE 3 COLUMNS TO FIX YOUR UI ---
    file_path = Column(String(255))      # Stores the filename (e.g. "abc_resume.pdf")
    resume_summary = Column(Text)       # Stores the AI's paragraph summary
    skills = Column(String(500))        # Stores the comma-separated skills
    # ------------------------------------------

    resume_text = Column(Text)          # Stores the full extracted text
    score = Column(Float)
    status = Column(String(50), default="Pending") 

    # Relationship back to the job
    job_post = relationship("JobPost", back_populates="candidates")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255)) 
    role = Column(String(20)) # "recruiter" or "candidate"