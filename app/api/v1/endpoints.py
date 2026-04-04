import os
import uuid
import time
import cloudinary
import cloudinary.uploader
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

# Internal Imports
from app.core.database import get_db
from app.models.candidate import JobPost, Candidate, User
from app.schemas.candidate import JobCreate, JobResponse, CandidateResponse
from app.services.ai_service import extract_text, calculate_match_score
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

# --- CLOUDINARY CONFIGURATION ---
# Ensure these are set in your Render Environment Variables
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "username": user.username, 
        "role": user.role
    }

@router.post("/signup")
def signup(username: str, password: str, role: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(username=username, password=hash_password(password), role=role)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# ---------------------------------------------------------
# JOB MANAGEMENT
# ---------------------------------------------------------

@router.post("/jobs/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = JobPost(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/jobs/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(JobPost).all()

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Cascade delete associated candidates
    db.query(Candidate).filter(Candidate.job_id == job_id).delete()
    db.delete(job)
    db.commit()
    return {"message": "Job and applications deleted"}

# ---------------------------------------------------------
# CANDIDATE & AI SCORING (CLOUDINARY INTEGRATED)
# ---------------------------------------------------------

@router.post("/apply/")
async def apply_job(
    job_id: int = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Prevent Duplicates
    existing = db.query(Candidate).filter(Candidate.job_id == job_id, Candidate.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already submitted for this job.")

    # 2. Cloudinary Upload
    try:
        file_content = await file.read()
        
        # Upload as 'raw' to preserve PDF structure
        upload_result = cloudinary.uploader.upload(
            file_content,
            resource_type="raw",
            folder="mindspark_resumes",
            public_id=f"resume_{uuid.uuid4()}"
        )
        permanent_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloud Storage Error: {str(e)}")

    # 3. AI Analysis
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Pass bytes to your AI service
    extracted_text = extract_text(file_content) 
    score = calculate_match_score(extracted_text, job.requirements)

    ai_summary = f"Candidate shows a {score}% match for the {job.title} role."

    # 4. Save to TiDB
    new_candidate = Candidate(
        job_id=job_id,
        full_name=full_name,
        email=email,
        file_path=permanent_url,  # Storing the full Cloudinary URL
        resume_text=extracted_text,
        resume_summary=ai_summary,
        skills="Extracted via AI Analysis",
        score=float(score),
        status="Pending"
    )
    
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    
    return {"message": "Application successful", "score": new_candidate.score}

# ---------------------------------------------------------
# RECRUITER & CANDIDATE VIEWS
# ---------------------------------------------------------

@router.get("/jobs/{job_id}/shortlist", response_model=List[CandidateResponse])
def get_shortlist(job_id: int, db: Session = Depends(get_db)):
    return db.query(Candidate).filter(Candidate.job_id == job_id).order_by(Candidate.score.desc()).all()

@router.put("/candidates/{candidate_id}/status")
def update_status(candidate_id: int, status: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.status = status
    db.commit()
    return {"message": f"Status updated to {status}"}

@router.get("/my-applications/{email}", response_model=List[CandidateResponse])
def get_my_apps(email: str, db: Session = Depends(get_db)):
    results = db.query(Candidate, JobPost.title).join(
        JobPost, Candidate.job_id == JobPost.id
    ).filter(Candidate.email == email).all()
    
    response_data = []
    for candidate, title in results:
        c_dict = CandidateResponse.from_orm(candidate)
        c_dict.job_title = title
        response_data.append(c_dict)
    return response_data