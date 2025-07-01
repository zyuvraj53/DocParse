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
    resume_metadata = Column(JSON)  # JSONB for metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    personal_information = relationship("PersonalInformation", uselist=False, back_populates="resume")
    education = relationship("Education", back_populates="resume")
    languages = relationship("Language", back_populates="resume")

class PersonalInformation(Base):
    __tablename__ = "personal_information"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)

    resume = relationship("Resume", back_populates="personal_information")

class Education(Base):
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    institution = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    field = Column(String, nullable=True)

    resume = relationship("Resume", back_populates="education")

class Language(Base):
    __tablename__ = "languages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=True)  # Changed to nullable=True to match database

    resume = relationship("Resume", back_populates="languages")


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_processed = Column(String, nullable=True)
    components = Column(JSON, nullable=True)  # JSONB for {"basic": 15000.0, "hra": 7000.0, ...}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    employment_proof = relationship("EmploymentProof", uselist=False, back_populates="payslip")

class EmploymentProof(Base):
    __tablename__ = "employment_proof"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payslip_id = Column(UUID(as_uuid=True), ForeignKey("payslips.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_name = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    valid = Column(String, nullable=True)  # Storing as String to match JSON's boolean as text

    payslip = relationship("Payslip", back_populates="employment_proof")

class ExperienceLetter(Base):
    __tablename__ = "experience_letters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_processed = Column(String, nullable=False)
    raw_text_length = Column(String, nullable=True)
    confidence_score = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    extracted_data = relationship("ExperienceLetterData", uselist=False, back_populates="experience_letter")
    formatting_consistency = relationship("ExperienceLetterFormatting", uselist=False, back_populates="experience_letter")
    anomalies = relationship("ExperienceLetterAnomaly", back_populates="experience_letter")

class ExperienceLetterData(Base):
    __tablename__ = "experience_letter_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experience_letter_id = Column(UUID(as_uuid=True), ForeignKey("experience_letters.id", ondelete="CASCADE"), unique=True, nullable=False)
    org_name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    employee_name = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    duration_years = Column(String, nullable=True)

    experience_letter = relationship("ExperienceLetter", back_populates="extracted_data")

class ExperienceLetterFormatting(Base):
    __tablename__ = "experience_letter_formatting"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experience_letter_id = Column(UUID(as_uuid=True), ForeignKey("experience_letters.id", ondelete="CASCADE"), unique=True, nullable=False)
    all_required_fields_present = Column(String, nullable=True)
    dates_valid = Column(String, nullable=True)
    dates_logical = Column(String, nullable=True)
    organization_name_valid = Column(String, nullable=True)
    job_title_valid = Column(String, nullable=True)
    employee_name_valid = Column(String, nullable=True)
    manager_info_present = Column(String, nullable=True)

    experience_letter = relationship("ExperienceLetter", back_populates="formatting_consistency")

class ExperienceLetterAnomaly(Base):
    __tablename__ = "experience_letter_anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experience_letter_id = Column(UUID(as_uuid=True), ForeignKey("experience_letters.id", ondelete="CASCADE"), nullable=False)
    anomaly_type = Column(String, nullable=False)
    description = Column(String, nullable=True)

    experience_letter = relationship("ExperienceLetter", back_populates="anomalies")