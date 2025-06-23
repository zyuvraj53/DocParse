from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from models import models
from schema import schemas
from config import database

from uuid import UUID
import shutil

router_resumes = APIRouter(prefix="/resumes", tags=["Resumes"])

@router_resumes.get("/", response_model=list[schemas.ResumeResponse])
async def get_resumes(db: Session = Depends(database.get_db)):
    resumes = db.query(models.Resume).all()
    return resumes

@router_resumes.post("/", response_model=schemas.ResumeResponse)
async def post_resume(resume: schemas.ResumeCreate, db: Session = Depends(database.get_db)):
    # Create resume
    db_resume = models.Resume(
        file_name=resume.file_name,
        skills=resume.skills,
        tools=resume.tools,
        concepts=resume.concepts,
        others=resume.others,
        resume_metadata=resume.resume_metadata.dict()
    )
    db.add(db_resume)
    db.flush()  # Get resume.id before committing

    # Create personal information
    db_personal_info = models.PersonalInformation(
        resume_id=db_resume.id,
        **resume.personal_information.dict()
    )
    db.add(db_personal_info)

    # Create education entries
    for edu in resume.education:
        db_education = models.Education(resume_id=db_resume.id, **edu.dict())
        db.add(db_education)

    # Create language entries
    for lang in resume.languages:
        db_language = models.Language(resume_id=db_resume.id, **lang.dict())
        db.add(db_language)

    db.commit()
    db.refresh(db_resume)
    return db_resume

@router_resumes.get("/{id}", response_model=schemas.ResumeResponse)
async def get_resume_by_id(id: UUID, db: Session = Depends(database.get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

import os

router_uploads = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

from typing import List


@router_uploads.post("/upload-resumes")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDF files
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file.size,
                "path": file_path
            })
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
    
    return {
        "message": f"Successfully uploaded {len(uploaded_files)} files",
        "files": uploaded_files
    }


from pdf_extractor.extractor import EnhancedPDFExtractor
from contextlib import redirect_stdout
import io
import traceback

@router_uploads.post("/process-resumes")
async def process_resumes(file: UploadFile = File(...)):
    try:
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        extractor = EnhancedPDFExtractor()
        sample_jd = "Software Engineer with Python and JavaScript experience"
        result = extractor.process_pdf(file_path, sample_jd, anonymize=True)
        return {
            "message": "Successfully processed resume",
            "status": "completed",
            "resumes": [result]
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )

@router_uploads.get("/")
async def root():
    return {"message": "Resume Parser API"}
