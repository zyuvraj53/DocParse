# def individual_resume_serial(resume: dict) -> dict:
#     return {
#         "id": str(resume["_id"]),
#         "file_name": resume["file_name"],
#         "personal_information": resume["personal_information"],
#         "education": resume.get("education", []),
#         "skills": resume.get("skills", {}),
#         "languages": resume.get("languages", []),
#         "tools": resume.get("tools", []),
#         "concepts": resume.get("concepts", []),
#         "others": resume.get("others", []),
#         "metadata": resume.get("metadata", {})
#     }

# def list_resume_serial(resumes: list) -> list:
#     return [individual_resume_serial(resume) for resume in resumes]

# def individual_personal_info_serial(info: dict) -> dict:
#     return {
#         "name": info.get("name"),
#         "email": info.get("email"),
#         "phone": info.get("phone"),
#         "location": info.get("location")
#     }

# def list_personal_info_serial(info_list: list) -> list:
#     return [individual_personal_info_serial(info) for info in info_list]


# def individual_education_serial(edu: dict) -> dict:
#     return {
#         "institution": edu.get("institution"),
#         "location": edu.get("location"),
#         "date": edu.get("date")
#     }

# def list_education_serial(education_list: list) -> list:
#     return [individual_education_serial(edu) for edu in education_list]

# def individual_language_serial(lang: dict) -> dict:
#     return {
#         "name": lang.get("name"),
#         "proficiency": lang.get("proficiency")
#     }

# def list_language_serial(language_list: list) -> list:
#     return [individual_language_serial(lang) for lang in language_list]
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

class PersonalInformationBase(BaseModel):
    """Base model for personal information."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class EducationBase(BaseModel):
    """Base model for education details."""
    institution: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None  # Expected format: e.g., "YYYY-MM-DD" or free-form

class LanguageBase(BaseModel):
    """Base model for language proficiency."""
    name: str
    proficiency: str  # Expected format: e.g., "Beginner", "Intermediate", "Advanced"

class MetadataBase(BaseModel):
    """Base model for resume metadata."""
    extracted_at: str  # ISO 8601 datetime string, e.g., "2025-06-22T15:50:45Z"
    anonymized: bool

    @validator("extracted_at")
    def validate_extracted_at(cls, v):
        """Validate that extracted_at is a valid ISO 8601 datetime string."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("extracted_at must be a valid ISO 8601 datetime string")
        return v

class ResumeCreate(BaseModel):
    """Model for creating a new resume."""
    file_name: str
    personal_information: PersonalInformationBase
    education: List[EducationBase]
    skills: Optional[Dict[str, List[str]]] = {}  # Allow empty skills dictionary
    languages: List[LanguageBase]
    tools: List[str]
    concepts: List[str]
    others: List[str]
    resume_metadata: MetadataBase

class ResumeResponse(BaseModel):
    """Model for resume response."""
    id: UUID
    file_name: str
    personal_information: PersonalInformationBase
    education: List[EducationBase]
    skills: Dict[str, List[str]]
    languages: List[LanguageBase]
    tools: List[str]
    concepts: List[str]
    others: List[str]
    resume_metadata: MetadataBase
    created_at: datetime

    class Config:
        from_attributes = True