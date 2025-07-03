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


from sqlalchemy import Column, String, Float, Integer, UUID, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
import uuid

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    gpa = Column(Float, nullable=True)
    graduation_date = Column(String, nullable=True)
    source_file = Column(String, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    text_length = Column(Integer, nullable=True)

    confidence_scores = relationship("Confidence_Scores", back_populates="certificate", cascade="all, delete-orphan", uselist=False)
    extraction_methods = relationship("Extraction_Methods", back_populates="certificate", cascade="all, delete-orphan", uselist=False)
    raw_matches_university = relationship("Raw_Matches_University", back_populates="certificate", cascade="all, delete-orphan")
    raw_matches_degree = relationship("Raw_Matches_Degree", back_populates="certificate", cascade="all, delete-orphan")
    raw_matches_gpa = relationship("Raw_Matches_GPA", back_populates="certificate", cascade="all, delete-orphan")
    raw_matches_graduation_date = relationship("Raw_Matches_Graduation_Date", back_populates="certificate", cascade="all, delete-orphan")
    extracted_entities_universities = relationship("Extracted_Entities_Universities", back_populates="certificate", cascade="all, delete-orphan")
    extracted_entities_organizations = relationship("Extracted_Entities_Organizations", back_populates="certificate", cascade="all, delete-orphan")
    extracted_entities_persons = relationship("Extracted_Entities_Persons", back_populates="certificate", cascade="all, delete-orphan")
    authenticity = relationship("Authenticity", back_populates="certificate", cascade="all, delete-orphan", uselist=False)
class Confidence_Scores(Base):
    __tablename__ = "confidence_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    university = Column(Float, nullable=True)
    degree = Column(Float, nullable=True)
    gpa = Column(Float, nullable=True)
    graduation_date = Column(Float, nullable=True)
    overall = Column(Float, nullable=True)

    certificate = relationship("Certificate", back_populates="confidence_scores")
class Extraction_Methods(Base):
    __tablename__ = "extraction_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    university = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    gpa = Column(String, nullable=True)
    graduation_date = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="extraction_methods")

class Raw_Matches_University(Base):
    __tablename__ = "raw_matches_university"  # Changed from "Raw_Matches_University"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    match = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="raw_matches_university")

class Raw_Matches_Degree(Base):
    __tablename__ = "raw_matches_degree"  # Changed from "Raw_Matches_Degree"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    match = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="raw_matches_degree")

class Raw_Matches_GPA(Base):
    __tablename__ = "raw_matches_gpa"  # Changed from "Raw_Matches_GPA"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    match = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="raw_matches_gpa")

class Raw_Matches_Graduation_Date(Base):
    __tablename__ = "raw_matches_graduation_date"  # Changed from "Raw_Matches_Graduation_Date"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    match = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="raw_matches_graduation_date")

class Extracted_Entities_Universities(Base):
    __tablename__ = "extracted_entities_universities"  # Changed from "Extracted_Entities_Universities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    university = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="extracted_entities_universities")

class Extracted_Entities_Organizations(Base):
    __tablename__ = "extracted_entities_organizations"  # Changed from "Extracted_Entities_Organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    organization = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="extracted_entities_organizations")

class Extracted_Entities_Persons(Base):
    __tablename__ = "extracted_entities_persons"  # Changed from "Extracted_Entities_Persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    person = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="extracted_entities_persons")
class Authenticity(Base):
    __tablename__ = "authenticity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False)
    overall_score = Column(Float, nullable=True)
    document_hash = Column(String, nullable=True)

    certificate = relationship("Certificate", back_populates="authenticity")
    digital_signatures = relationship("Digital_Signatures", back_populates="authenticity", cascade="all, delete-orphan")
    qr_codes = relationship("QR_Codes", back_populates="authenticity", cascade="all, delete-orphan")
    qr_verification = relationship("QR_Verification", back_populates="authenticity", cascade="all, delete-orphan")
    authenticity_indicators = relationship("Authenticity_Indicators", back_populates="authenticity", cascade="all, delete-orphan")
    risk_factors = relationship("Risk_Factors", back_populates="authenticity", cascade="all, delete-orphan")
    recommendations = relationship("Recommendations", back_populates="authenticity")

class Digital_Signatures(Base):
    __tablename__ = "digital_signatures"  # Changed from "Digital_Signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticity_id = Column(UUID(as_uuid=True), ForeignKey("authenticity.id"), nullable=False)
    has_digital_signature = Column(Boolean, nullable=True)
    signature_count = Column(Integer, nullable=True)
    encrypted = Column(Boolean, nullable=True)
    error = Column(String, nullable=True)

    authenticity = relationship("Authenticity", back_populates="digital_signatures")
    certificate_metadata = relationship("Certificate_Metadata", back_populates="digital_signatures", cascade="all, delete-orphan")
    security_features = relationship("Security_Features", back_populates="digital_signatures", cascade="all, delete-orphan")

class Certificate_Metadata(Base):
    __tablename__ = "certificate_metadata"  # Changed from "Certificate_Metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    digital_signature_id = Column(UUID(as_uuid=True), ForeignKey("digital_signatures.id"), nullable=False)
    creator = Column(String, nullable=True)
    producer = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    author = Column(String, nullable=True)
    creation_date = Column(String, nullable=True)
    modification_date = Column(String, nullable=True)

    digital_signatures = relationship("Digital_Signatures", back_populates="certificate_metadata")

class Security_Features(Base):
    __tablename__ = "security_features"  # Changed from "Security_Features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    digital_signature_id = Column(UUID(as_uuid=True), ForeignKey("digital_signatures.id"), nullable=False)
    feature = Column(String, nullable=True)

    digital_signatures = relationship("Digital_Signatures", back_populates="security_features")

class QR_Codes(Base):
    __tablename__ = "qr_codes"  # Changed from "QR_Codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticity_id = Column(UUID(as_uuid=True), ForeignKey("authenticity.id"), nullable=False)
    qr_code = Column(String, nullable=True)

    authenticity = relationship("Authenticity", back_populates="qr_codes")

class QR_Verification(Base):
    __tablename__ = "qr_verification"  # Changed from "QR_Verification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticity_id = Column(UUID(as_uuid=True), ForeignKey("authenticity.id"), nullable=False)
    verification = Column(String, nullable=True)

    authenticity = relationship("Authenticity", back_populates="qr_verification")

class Authenticity_Indicators(Base):
    __tablename__ = "authenticity_indicators"  # Changed from "Authenticity_Indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticity_id = Column(UUID(as_uuid=True), ForeignKey("authenticity.id"), nullable=False)
    indicator = Column(String, nullable=True)

    authenticity = relationship("Authenticity", back_populates="authenticity_indicators")

class Risk_Factors(Base):
    __tablename__ = "risk_factors"  # Changed from "Risk_Factors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticity_id = Column(UUID(as_uuid=True), ForeignKey("authenticity.id"), nullable=False)
    risk_factor = Column(String, nullable=True)

    authenticity = relationship("Authenticity", back_populates="risk_factors")

class Recommendations(Base):
    __tablename__ = "recommendations"  # Changed from "Recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticity_id = Column(UUID(as_uuid=True), ForeignKey("authenticity.id"), nullable=False)
    recommendation = Column(String, nullable=True)

    authenticity = relationship("Authenticity", back_populates="recommendations")
