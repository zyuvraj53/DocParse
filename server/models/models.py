from sqlalchemy import Column, String, JSON, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from config.database import Base
import uuid
from sqlalchemy.sql import func

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    skills = Column(JSON)  # JSONB for {"category": ["skill1", "skill2"]}
    tools = Column(ARRAY(String))  # Array of strings
    concepts = Column(ARRAY(String))  # Array of strings
    others = Column(ARRAY(String))  # Array of strings
    resume_metadata = Column(JSON)  # Renamed from 'metadata' to avoid conflict
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    personal_information = relationship("PersonalInformation", uselist=False, back_populates="resume")
    education = relationship("Education", back_populates="resume")
    languages = relationship("Language", back_populates="resume")

class PersonalInformation(Base):
    __tablename__ = "personal_information"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    location = Column(String)

    resume = relationship("Resume", back_populates="personal_information")

class Education(Base):
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String)
    location = Column(String)
    date = Column(String)

    resume = relationship("Resume", back_populates="education")

class Language(Base):
    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    proficiency = Column(String, nullable=False)

    resume = relationship("Resume", back_populates="languages")