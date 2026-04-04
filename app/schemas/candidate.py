from pydantic import BaseModel, EmailStr
from typing import List, Optional

class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str

class JobResponse(JobCreate):
    id: int
    class Config:
        from_attributes = True

class CandidateResponse(BaseModel):
    id: int
    job_id: int
    full_name: str
    email: EmailStr
    score: float
    status: str = "Pending"
    
    # --- ADD THESE 4 FIELDS TO FIX YOUR DASHBOARD ---
    file_path: Optional[str] = None       # Fixes "No PDF found"
    resume_text: Optional[str] = None     # Fixes "No text"
    resume_summary: Optional[str] = None  # Fixes "Summary: N/A"
    skills: Optional[str] = None          # Fixes "Skills: N/A"
    # -----------------------------------------------
    
    job_title: Optional[str] = None 

    class Config:
        from_attributes = True