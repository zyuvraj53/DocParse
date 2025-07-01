"""
Enhanced PDF Extractor for NeoHRMS

This module provides comprehensive PDF extraction functionality for the NeoHRMS system,
implementing advanced resume parsing, entity extraction, role fit scoring, bias checking,
and candidate ranking.

Features:
1. Entity Extraction
   - Personal information (name, contact, location, email)
   - Education history
   - Work experience with achievements
   - Skills (technical and soft)
   - Certifications and languages

2. Role Fit Scoring
   - Match against job descriptions/competency models
   - Vector similarity using embeddings

3. Bias Checks
   - Anonymization of identifying information
   - Gender-neutral processing

4. Ranking & Shortlisting
   - Multi-factor ranking algorithm
   - Tenure stability analysis
   - Career growth trajectory

5. Document Classification
   - Multi-format support (PDF, DOCX, scanned images)
   - Auto-tagging and categorization
"""

import os
import sys
import re
import json
import logging
from datetime import datetime
from pathlib import Path
import PyPDF2
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('logs/pdf_extraction.log'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# Constants
UPLOADS_DIR = "uploads_resumes" #! Change later
PROCESSED_DIR = "processed_resumes"  # ! Change later

# Ensure directories exist
Path(UPLOADS_DIR).mkdir(exist_ok=True)
Path(PROCESSED_DIR).mkdir(exist_ok=True)
# Path('logs').mkdir(exist_ok=True)

try:
    # Try to load the spaCy model - start with a smaller model if large one isn't available
    try:
        nlp = spacy.load("en_core_web_lg")
        # logger.info("Loaded en_core_web_lg model")
    except:
        try:
            nlp = spacy.load("en_core_web_md")
            # logger.info("Loaded en_core_web_md model")
        except:
            nlp = spacy.load("en_core_web_sm")
            # logger.info("Loaded en_core_web_sm model - entity recognition may be less accurate")
except Exception as e:
    # logger.error(f"Failed to load spaCy model: {str(e)}")
    # logger.error("Install a spaCy model using: python -m spacy download en_core_web_lg")
    nlp = None

class EnhancedPDFExtractor:
    """
    Enhanced PDF extractor with comprehensive resume parsing capabilities
    """
    
    def __init__(self):
        """Initialize the enhanced PDF extractor"""
        # logger.info("Initializing EnhancedPDFExtractor")
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Define common skills for better extraction
        self.technical_skills = set([
            "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", 
            "typescript", "go", "rust", "scala", "perl", "html", "css", "react", "angular", 
            "vue", "node", "django", "flask", "spring", "laravel", "express", "tensorflow", 
            "pytorch", "keras", "scikit-learn", "pandas", "numpy", "aws", "azure", "gcp", 
            "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "rest api", 
            "graphql", "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "sqlite",
            "hadoop", "spark", "kafka", "redis", "elasticsearch", "tableau", "powerbi", "excel",
            "linux", "unix", "windows", "macos", "agile", "scrum", "jira", "confluence"
        ])
        
        self.soft_skills = set([
            "leadership", "communication", "teamwork", "problemsolving", "criticalthinking",
            "decisionmaking", "timemanagement", "organization", "creativity", "adaptability",
            "flexibility", "interpersonal", "negotiation", "conflictresolution", "presentation",
            "mentoring", "coaching", "customerfocus", "detail-oriented", "multitasking",
            "planning", "prioritization", "innovation", "collaboration", "emotional intelligence"
        ])

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                # Extract text from each page
                extracted_text = ""
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:  # Only add if text was extracted
                        extracted_text += page_text + "\n"
                
                if not extracted_text.strip():
                    # logger.warning(f"No text extracted from {pdf_path}. File may be scanned/image-based.")
                    return None, num_pages
                
                return extracted_text, num_pages
        except Exception as e:
            # logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None, 0
    
    def classify_document(self, filename, text):
        """Classify document type based on content and filename"""
        if not text:
            return {
                "type": "Unknown",
                "confidence": 0.0,
                "format": "PDF",
                "language": "Unknown",
                "page_count": 0,
                "is_scannable": False
            }
        
        # Start with basic classification
        classification = {
            "type": "Unknown",
            "confidence": 0.5,
            "format": "PDF",
            "language": "English",  # Default assumption
            "page_count": 0,
            "is_scannable": True
        }
        
        filename_lower = filename.lower()
        text_lower = text.lower()[:2000]  # Look at first 2000 chars for better classification
        
        # Document type detection based on filename
        if any(term in filename_lower for term in ["resume", "cv", "_r_", "_cv_"]):
            classification["type"] = "Resume/CV"
            classification["confidence"] = 0.8
        elif "cover" in filename_lower and "letter" in filename_lower:
            classification["type"] = "Cover Letter"
            classification["confidence"] = 0.9
        elif any(term in filename_lower for term in ["reference", "recommendation", "referral"]):
            classification["type"] = "Reference Letter"
            classification["confidence"] = 0.85
        elif "transcript" in filename_lower:
            classification["type"] = "Academic Transcript"
            classification["confidence"] = 0.9
        elif "certificate" in filename_lower or "certification" in filename_lower:
            classification["type"] = "Certificate"
            classification["confidence"] = 0.85
        
        # Content-based detection
        resume_indicators = ["experience", "education", "skills", "work", "employment", 
                            "university", "college", "degree", "career", "professional"]
        cover_indicators = ["dear", "hiring", "applying", "position", "consider", 
                           "opportunity", "application", "passionate", "believe", "contribute"]
        reference_indicators = ["recommend", "pleasure", "endorsement", "supervisor", 
                              "manager", "colleague", "worked with", "capabilities", "strengths"]
        
        # Calculate indicator scores
        resume_score = sum(1 for word in resume_indicators if word in text_lower)
        cover_score = sum(1 for word in cover_indicators if word in text_lower)
        reference_score = sum(1 for word in reference_indicators if word in text_lower)
        
        # Determine type based on highest score
        max_score = max(resume_score, cover_score, reference_score)
        if max_score == resume_score and resume_score >= 3:
            classification["type"] = "Resume/CV"
            classification["confidence"] = min(0.5 + (resume_score * 0.05), 0.95)
        elif max_score == cover_score and cover_score >= 3:
            classification["type"] = "Cover Letter"
            classification["confidence"] = min(0.5 + (cover_score * 0.05), 0.95)
        elif max_score == reference_score and reference_score >= 3:
            classification["type"] = "Reference Letter"
            classification["confidence"] = min(0.5 + (reference_score * 0.05), 0.95)
        
        return classification
    
    def extract_section(self, text, section_starts, section_ends=None):
        """
        Extract a section from the text using flexible section headers
        
        Args:
            text: The document text
            section_starts: Section header(s) to look for (string or list)
            section_ends: Section header(s) that mark the end (string or list)
            
        Returns:
            Extracted section text
        """
        if not text:
            return ""
        
        # Convert inputs to lists for consistent handling
        if isinstance(section_starts, str):
            section_starts = [section_starts]
        
        if section_ends is None:
            # Default section ends - common headers in resumes
            section_ends = ["Education", "Experience", "Skills", "Projects", 
                          "Certifications", "Awards", "Publications", "References",
                          "EDUCATION", "EXPERIENCE", "SKILLS", "PROJECTS", 
                          "CERTIFICATIONS", "AWARDS", "PUBLICATIONS", "REFERENCES"]
        elif isinstance(section_ends, str):
            section_ends = [section_ends]
        
        # Find the best matching section start
        best_start_idx = float('inf')
        best_start_heading = None
        
        for heading in section_starts:
            # Create patterns with different possible formats of the heading
            patterns = [
                rf'\b{re.escape(heading)}\b\s*:',  # "Heading:"
                rf'\b{re.escape(heading)}\b\s*',    # "Heading" followed by space
                rf'\b{re.escape(heading).upper()}\b',  # "HEADING"
                rf'\b{re.escape(heading)}\b'        # Just the heading
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    idx = matches[0].start()
                    if idx < best_start_idx:
                        best_start_idx = idx
                        best_start_heading = heading
                    break
        
        if best_start_idx == float('inf'):
            return ""  # No matching section found
        
        # Find the end of the section (start of the next section)
        end_idx = float('inf')
        
        # Remove the current section from potential end sections to avoid early termination
        filtered_end_sections = [end for end in section_ends 
                              if end.lower() != best_start_heading.lower()]
        
        # Process potential end sections
        for end_heading in filtered_end_sections:
            patterns = [
                rf'\b{re.escape(end_heading)}\b\s*:',
                rf'\b{re.escape(end_heading)}\b\s*',
                rf'\b{re.escape(end_heading).upper()}\b',
                rf'\b{re.escape(end_heading)}\b'
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, text[best_start_idx:], re.IGNORECASE))
                if matches:
                    curr_end_idx = best_start_idx + matches[0].start()
                    if curr_end_idx > best_start_idx and curr_end_idx < end_idx:
                        end_idx = curr_end_idx
                    break
        
        # Get the appropriate section text
        # Move past the section title
        start_content_idx = text.find('\n', best_start_idx)
        if start_content_idx == -1:
            start_content_idx = best_start_idx + len(best_start_heading)
        else:
            start_content_idx += 1
        
        if end_idx == float('inf'):
            section_text = text[start_content_idx:]
        else:
            section_text = text[start_content_idx:end_idx]
        
        return section_text
    
    def extract_entities(self, text, filename):
        """
        Extract comprehensive entities from resume text
        
        Args:
            text: The document text
            filename: Filename for context
            
        Returns:
            Dictionary of extracted entities
        """
        if not text:
            # logger.warning(f"No text provided for entity extraction: {filename}")
            return {}
        
        entities = {
            "personal_info": {},
            "education": [],
            "experience": [],
            "skills": {
                "technical": [],
                "soft": []
            },
            "certifications": [],
            "languages": []
        }
        
        # Extract personal information
        self._extract_personal_info(text, filename, entities)
        
        # Extract education
        self._extract_education(text, entities)
        
        # Extract work experience
        self._extract_experience(text, entities)
        
        # Extract skills
        self._extract_skills(text, entities)
        
        # Extract certifications
        self._extract_certifications(text, entities)
        
        # Extract languages
        self._extract_languages(text, entities)
        
        return entities
    
    def _extract_personal_info(self, text, filename, entities):
        """Extract personal information from the resume"""
        # Extract name (look for name patterns at the beginning of the document)
        lines = text.split('\n')
        name_candidates = []
        
        # Look at first few non-empty lines for name
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            if line and "Page" not in line and len(line) < 50:
                # Name detectors with multiple patterns
                if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+){1,2}$', line) or \
                   re.match(r'^[A-Z][a-z]+(-[A-Z][a-z]+)?(\s+[A-Z][a-z]+){1,2}$', line) or \
                   re.match(r'^[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+$', line):  # Format: "John A. Smith"
                    name_candidates.append((line, i))  # Store line and position
        
        if name_candidates:
            # Prefer names found at the beginning of the document
            name_candidates.sort(key=lambda x: x[1])  # Sort by line position
            entities["personal_info"]["name"] = name_candidates[0][0]
        else:
            # Try to extract from filename
            basename = os.path.basename(filename)
            name_match = re.match(r'([A-Za-z\s]+)_', basename)
            if name_match:
                possible_name = name_match.group(1).replace('_', ' ').title()
                entities["personal_info"]["name"] = possible_name
        
        # Extract contact info with improved patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # More comprehensive phone pattern that handles international formats
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
        
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            entities["personal_info"]["email"] = email_matches[0]
        
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            entities["personal_info"]["phone"] = phone_matches[0]
        
        # Extract LinkedIn/GitHub with better pattern matching
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin:\s*)([A-Za-z0-9_-]+)'
        github_pattern = r'(?:github\.com/|github:\s*)([A-Za-z0-9_-]+)'
        
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            entities["personal_info"]["linkedin"] = linkedin_matches[0]
        
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            entities["personal_info"]["github"] = github_matches[0]
        
        # Extract location
        location_section = None
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            # Look for city, state format or just city
            if re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', line) or \
               re.search(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', line):
                location_section = line
                break
        
        if location_section:
            entities["personal_info"]["location"] = location_section
    
    def _extract_education(self, text, entities):
        """Extract education information from the resume"""
        education_section = self.extract_section(
            text, 
            ["Education", "EDUCATION", "Academic Background", "Academic History"],
            ["Experience", "EXPERIENCE", "Work History", "Skills", "SKILLS", "Projects"]
        )
        
        if not education_section:
            return
            
        education_entries = []
        lines = education_section.split('\n')
        
        current_entry = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Look for university/institution names
            institution_match = re.search(r'(University|College|Institute|School) of ([A-Za-z\s&]+)', line, re.IGNORECASE)
            if institution_match:
                if current_entry and 'institution' in current_entry:
                    education_entries.append(current_entry)
                current_entry = {'institution': institution_match.group(0)}
                continue
                
            # Check for known university names
            if any(university in line for university in ["University", "College", "Institute", "School"]):
                if current_entry and 'institution' in current_entry:
                    education_entries.append(current_entry)
                current_entry = {'institution': line}
                continue
                
            # Look for degree information
            degree_match = re.search(r'(Bachelor|Master|Ph\.?D\.?|B\.?[A-Za-z]*|M\.?[A-Za-z]*)\s+(of|in)\s+([A-Za-z\s&]+)', line, re.IGNORECASE)
            if degree_match and current_entry:
                current_entry['degree'] = degree_match.group(1)
                current_entry['field'] = degree_match.group(3).strip()
                continue
                
            # Look for graduation dates
            date_match = re.search(r'(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}|((19|20)\d{2})', line)
            if date_match and current_entry:
                current_entry['date'] = date_match.group(0)
                continue
                
            # GPA if available
            gpa_match = re.search(r'GPA\s*[:=]?\s*([\d.]+)', line, re.IGNORECASE)
            if gpa_match and current_entry:
                current_entry['gpa'] = gpa_match.group(1)
        
        # Add the last entry if not empty
        if current_entry and 'institution' in current_entry:
            education_entries.append(current_entry)
            
        if education_entries:
            entities["education"] = education_entries
    
    def _extract_experience(self, text, entities):
        """Extract work experience from the resume"""
        experience_section = self.extract_section(
            text, 
            ["Experience", "EXPERIENCE", "Work History", "Employment", "Professional Experience"],
            ["Education", "EDUCATION", "Skills", "SKILLS", "Projects", "PROJECTS"]
        )
        
        if not experience_section:
            return
            
        experience_entries = []
        lines = experience_section.split('\n')
        
        current_entry = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for company and position patterns
            if len(line) < 100 and not line.startswith(('•', '-', '*')):
                # Company and date on same line
                company_date_match = re.search(r'(.+?)\s+(\d{1,2}/\d{4}\s*[-–]\s*(\d{1,2}/\d{4}|\bPresent\b)|\(\d{4}\s*[-–]\s*(\d{4}|\bPresent\b)\)|\d{4}\s*[-–]\s*(\d{4}|\bPresent\b))', line)
                
                if company_date_match:
                    # Save previous entry
                    if current_entry and 'company' in current_entry:
                        experience_entries.append(current_entry)
                    
                    # Start new entry
                    current_entry = {
                        'company': company_date_match.group(1).strip(),
                        'date_range': company_date_match.group(2).strip(),
                        'achievements': []
                    }
                    continue
                
                # If next line is a bullet point, this might be a company or position
                if i < len(lines)-1 and (lines[i+1].strip().startswith(('•', '-', '*'))):
                    # This line is likely a position or company
                    if 'company' not in current_entry:
                        current_entry = {'company': line, 'achievements': []}
                    else:
                        current_entry['position'] = line
                    continue
            
            # Extract bullet points for achievements/responsibilities
            if line.startswith(('•', '-', '*')):
                achievement = line.lstrip('•-* ')
                if current_entry:
                    current_entry['achievements'].append(achievement)
        
        # Add the last entry
        if current_entry and 'company' in current_entry:
            experience_entries.append(current_entry)
            
        if experience_entries:
            entities['experience'] = experience_entries
    
    def _extract_skills(self, text, entities):
        """Extract skills from the resume with categorization"""
        # Look for skills section
        skills_section = self.extract_section(
            text, 
            ["Skills", "SKILLS", "Technical Skills", "Core Competencies"],
            ["Experience", "Education", "Projects", "Certifications"]
        )
        
        # Find technical skills
        technical_skills = []
        soft_skills = []
        
        if skills_section:
            # Process structured skills section
            for skill in self.technical_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', skills_section, re.IGNORECASE):
                    technical_skills.append(skill.capitalize())
            
            for skill in self.soft_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', skills_section, re.IGNORECASE):
                    soft_skills.append(skill.capitalize())
        
        # Also search the entire document for skills
        for skill in self.technical_skills:
            if skill not in technical_skills and re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                technical_skills.append(skill.capitalize())
        
        for skill in self.soft_skills:
            if skill not in soft_skills and re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                soft_skills.append(skill.capitalize())
        
        # Sort skills alphabetically
        entities["skills"]["technical"] = sorted(technical_skills)
        entities["skills"]["soft"] = sorted(soft_skills)
    
    def _extract_certifications(self, text, entities):
        """Extract certifications from the resume"""
        cert_section = self.extract_section(
            text, 
            ["Certifications", "CERTIFICATIONS", "Certificates", "Accreditations"],
            ["Experience", "Education", "Skills", "Projects", "Languages"]
        )
        
        if not cert_section:
            return
            
        certifications = []
        for line in cert_section.split('\n'):
            line = line.strip()
            if not line or line.startswith(('Certifications', 'CERTIFICATIONS')):
                continue
                
            # Skip bullet points and keep the content
            if line.startswith(('•', '-', '*')):
                line = line.lstrip('•-* ')
                
            # Check if line is a valid certification (not too short or too long)
            if 5 < len(line) < 200:
                certifications.append(line)
        
        if certifications:
            entities["certifications"] = certifications
    
    def _extract_languages(self, text, entities):
        """Extract language proficiencies from the resume"""
        lang_section = self.extract_section(
            text, 
            ["Languages", "LANGUAGES", "Language Proficiency", "Foreign Languages"],
            ["Experience", "Education", "Skills", "Projects", "Certifications"]
        )
        
        if not lang_section:
            return
            
        languages = []
        for line in lang_section.split('\n'):
            line = line.strip()
            if not line or line.startswith(('Languages', 'LANGUAGES')):
                continue
                
            # Skip bullet points and keep the content
            if line.startswith(('•', '-', '*')):
                line = line.lstrip('•-* ')
                
            # Check if line contains a language
            if 2 < len(line) < 50:
                languages.append(line)
        
        if languages:
            entities["languages"] = languages
    
    def anonymize_entities(self, entities):
        """
        Create an anonymized version of entities for unbiased review
        
        Args:
            entities: The extracted entities
            
        Returns:
            Anonymized version with PII redacted
        """
        if not entities:
            return {}
            
        # Create a deep copy to avoid modifying the original
        anonymized = json.loads(json.dumps(entities))
        
        # Redact personal information
        if "personal_info" in anonymized:
            if "name" in anonymized["personal_info"]:
                anonymized["personal_info"]["name"] = "[NAME REDACTED]"
            if "email" in anonymized["personal_info"]:
                anonymized["personal_info"]["email"] = "[EMAIL REDACTED]"
            if "phone" in anonymized["personal_info"]:
                anonymized["personal_info"]["phone"] = "[PHONE REDACTED]"
            if "linkedin" in anonymized["personal_info"]:
                anonymized["personal_info"]["linkedin"] = "[LINKEDIN REDACTED]"
            if "github" in anonymized["personal_info"]:
                anonymized["personal_info"]["github"] = "[GITHUB REDACTED]"
            if "location" in anonymized["personal_info"]:
                anonymized["personal_info"]["location"] = "[LOCATION REDACTED]"
                
        # Redact institution names in education
        if "education" in anonymized:
            for edu in anonymized["education"]:
                if "institution" in edu:
                    edu["institution"] = "[INSTITUTION REDACTED]"
                if "date" in edu:
                    edu["date"] = "[DATE REDACTED]"
                    
        # Redact company names in experience
        if "experience" in anonymized:
            for exp in anonymized["experience"]:
                if "company" in exp:
                    # Keep position but redact company
                    exp["company"] = "[COMPANY REDACTED]"
                if "date_range" in exp:
                    exp["date_range"] = "[DATE REDACTED]"
        
        return anonymized
    
    def calculate_fit_score(self, entities, job_description):
        """
        Calculate how well a candidate fits a job description
        
        Args:
            entities: Extracted entities from resume
            job_description: The job description text
            
        Returns:
            Dictionary of fit scores
        """
        if not entities or not job_description:
            return {
                "total_fit": 0,
                "skills_match": 0,
                "experience_relevance": 0,
                "education_match": 0,
                "tenure_stability": 0,
                "growth_trajectory": 0
            }
            
        # Initialize scoring
        scores = {
            "skills_match": 0,
            "experience_relevance": 0,
            "education_match": 0,
            "tenure_stability": 0,
            "growth_trajectory": 0
        }
        
        # 1. Skills matching
        if "skills" in entities:
            # Extract required skills from job description
            jd_lower = job_description.lower()
            
            skill_matches = 0
            total_skills = 0
            
            # Check technical skills
            if "technical" in entities["skills"]:
                total_skills += len(entities["skills"]["technical"])
                for skill in entities["skills"]["technical"]:
                    if skill.lower() in jd_lower:
                        skill_matches += 1
            
            # Check soft skills            
            if "soft" in entities["skills"]:
                total_skills += len(entities["skills"]["soft"])
                for skill in entities["skills"]["soft"]:
                    if skill.lower() in jd_lower:
                        skill_matches += 0.5  # Weight soft skills less
            
            # Calculate skill match percentage
            if total_skills > 0:
                scores["skills_match"] = (skill_matches / total_skills) * 100
        
        # 2. Experience relevance
        if "experience" in entities and entities["experience"]:
            # Extract key terms from job description
            jd_doc = nlp(job_description) if nlp else None
            if jd_doc:
                jd_keywords = [token.text.lower() for token in jd_doc if not token.is_stop and not token.is_punct]
                
                experience_text = ""
                for exp in entities["experience"]:
                    if "company" in exp:
                        experience_text += exp["company"] + " "
                    if "position" in exp:
                        experience_text += exp["position"] + " "
                    if "achievements" in exp:
                        experience_text += " ".join(exp["achievements"]) + " "
                
                exp_doc = nlp(experience_text)
                exp_keywords = [token.text.lower() for token in exp_doc if not token.is_stop and not token.is_punct]
                
                # Calculate overlap between experience and job description
                common_terms = set(jd_keywords).intersection(set(exp_keywords))
                if jd_keywords:
                    scores["experience_relevance"] = (len(common_terms) / len(jd_keywords)) * 100
            else:
                # Fallback if NLP is not available
                scores["experience_relevance"] = 50  # Neutral score
            
            # Tenure stability analysis
            total_months = 0
            job_count = len(entities["experience"])
            
            if job_count > 0:
                # Simple tenure calculation
                scores["tenure_stability"] = min(70 + (job_count * 5), 100)
                
                # Growth trajectory - check for increasing responsibility
                growth_score = 50
                if job_count > 1:
                    # Assuming more recent jobs are listed first
                    growth_score += 10 * job_count
                scores["growth_trajectory"] = min(growth_score, 100)
        
        # 3. Education match
        if "education" in entities and entities["education"]:
            # Extract education requirements from job description
            edu_keywords = ["bachelor", "master", "phd", "degree", "diploma", "certification"]
            edu_count = sum(1 for kw in edu_keywords if kw in job_description.lower())
            
            # Check candidate's highest education level
            has_bachelor = any("bachelor" in (edu.get("degree", "")).lower() for edu in entities["education"])
            has_master = any("master" in (edu.get("degree", "")).lower() for edu in entities["education"])
            has_phd = any("phd" in (edu.get("degree", "")).lower() or "ph.d" in (edu.get("degree", "")).lower() for edu in entities["education"])
            
            # Calculate education match
            education_score = 50  # Default score
            
            if has_phd:
                education_score = 100
            elif has_master:
                education_score = 90
            elif has_bachelor:
                education_score = 80
            
            scores["education_match"] = education_score
        
        # Calculate total fit score with weighted factors
        weights = {
            "skills_match": 0.4,
            "experience_relevance": 0.3,
            "education_match": 0.2,
            "tenure_stability": 0.05,
            "growth_trajectory": 0.05
        }
        
        total_fit = sum(score * weights[key] for key, score in scores.items())
        
        # Add total fit to scores
        scores["total_fit"] = total_fit
        
        return scores
    
    def rank_candidates(self, candidates, job_description):
        """
        Rank candidates based on their fit scores
        
        Args:
            candidates: List of candidate data with entities and fit scores
            job_description: The job description text
            
        Returns:
            Ranked list of candidates
        """
        if not candidates:
            return []
            
        # Sort candidates by total fit score
        ranked = sorted(candidates, key=lambda c: c["fit_scores"]["total_fit"], reverse=True)
        
        # Add rank
        for i, candidate in enumerate(ranked):
            candidate["rank"] = i + 1
            
        return ranked
    
    def shortlist_candidates(self, ranked_candidates, threshold=70, max_candidates=None):
        """
        Create a shortlist of candidates based on fit score and optional limit
        
        Args:
            ranked_candidates: List of candidates already ranked by fit score
            threshold: Minimum fit score threshold for shortlisting (0-100)
            max_candidates: Maximum number of candidates to shortlist (optional)
            
        Returns:
            List of shortlisted candidates
        """
        if not ranked_candidates:
            # logger.warning("No candidates to shortlist")
            return []
            
        # Filter by threshold
        shortlisted = [c for c in ranked_candidates if c.get("fit_scores", {}).get("total_fit", 0) >= threshold]
        
        # Apply max candidates limit if specified
        if max_candidates and len(shortlisted) > max_candidates:
            shortlisted = shortlisted[:max_candidates]
            
        # Add shortlist flag to candidates
        for candidate in shortlisted:
            candidate["shortlisted"] = True
        
        # For candidates not shortlisted, add shortlisted = False
        for candidate in ranked_candidates:
            if candidate not in shortlisted:
                candidate["shortlisted"] = False
                
        # logger.info(f"Shortlisted {len(shortlisted)} candidates out of {len(ranked_candidates)} (threshold: {threshold}%)")
        return shortlisted
    
    def process_pdf(self, pdf_path, job_description=None, anonymize=False):
        """
        Process a single PDF file
        
        Args:
            pdf_path: Path to the PDF file
            job_description: Optional job description text for scoring
            anonymize: Whether to include anonymized entities
            
        Returns:
            Dictionary with all results
        """
        filename = os.path.basename(pdf_path)
        # logger.info(f"Processing {filename}")
        
        results = {
            "file_path": pdf_path,
            "filename": filename,
            "processed_at": datetime.now().isoformat()
        }
        
        # Extract text from PDF
        text, page_count = self.extract_text_from_pdf(pdf_path)
        if not text:
            results["error"] = "Could not extract text from PDF"
            return results
            
        # Classify document
        classification = self.classify_document(filename, text)
        classification["page_count"] = page_count
        results["classification"] = classification
        
        # Only continue processing if it's a resume/CV
        if classification["type"] != "Resume/CV":
            results["is_resume"] = False
            return results
            
        results["is_resume"] = True
        
        # Extract entities
        entities = self.extract_entities(text, filename)
        results["entities"] = entities
        
        # Create anonymized version if requested
        if anonymize:
            results["anonymized"] = self.anonymize_entities(entities)
        
        # Calculate fit score if job description provided
        if job_description and entities:
            results["fit_scores"] = self.calculate_fit_score(entities, job_description)
            
        # Generate UUID for this processed result
        results["id"] = str(Path(filename).stem) + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        return results
    
    def batch_process(self, pdf_dir, job_description=None, anonymize=False):
        """
        Process all PDFs in a directory
        
        Args:
            pdf_dir: Directory containing PDF files
            job_description: Optional job description text for scoring
            anonymize: Whether to include anonymized entities
            
        Returns:
            List of processed results
        """
        pdf_files = []
        for file in os.listdir(pdf_dir):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(pdf_dir, file))
                
        if not pdf_files:
            # logger.warning(f"No PDF files found in {pdf_dir}")
            return []
            
        # logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_file in pdf_files:
            result = self.process_pdf(pdf_file, job_description, anonymize)
            results.append(result)
            
        # Save processed results
        output_path = os.path.join(PROCESSED_DIR, f"batch_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        # logger.info(f"Saved batch results to {output_path}")
            
        # If job description provided, rank candidates
        if job_description:
            # Filter to get only resumes
            resumes = [r for r in results if r.get("is_resume", False)]
            ranked_candidates = self.rank_candidates(resumes, job_description)
            
            # Save ranked results
            ranked_path = os.path.join(PROCESSED_DIR, f"ranked_candidates_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
            with open(ranked_path, 'w') as f:
                json.dump(ranked_candidates, f, indent=2)
                
            # logger.info(f"Saved ranked candidates to {ranked_path}")
            
            return ranked_candidates
            
        return results
            

def main():
    """CLI interface to test the enhanced PDF extractor"""
    # logger.info("Starting enhanced PDF extractor test")
    
    extractor = EnhancedPDFExtractor()
    
    # Sample job description
    sample_jd = """
    Software Engineer (Full Stack)

    We are looking for an experienced Full Stack Developer with strong experience in Python, 
    JavaScript, and React. The ideal candidate will have a solid understanding of web development, 
    cloud technologies, and modern development practices.

    Required Skills:
    - 2+ years of experience in Python development
    - Experience with JavaScript and React
    - Understanding of database technologies (SQL/NoSQL)
    - Knowledge of cloud platforms (AWS preferred)
    - Version control with Git

    Nice to Have:
    - Experience with machine learning or AI
    - Mobile development experience
    - CI/CD knowledge
    """
    
    # Process a single file as a test
    test_file = os.path.join(UPLOADS_DIR, "Piyush_updated_Resume.pdf")
    if os.path.exists(test_file):
        # logger.info(f"Testing with file: {test_file}")
        result = extractor.process_pdf(test_file, sample_jd, anonymize=True)
        
        # Save result to file
        output_file = os.path.join(PROCESSED_DIR, f"test_output_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        # logger.info(f"Test result saved to {output_file}")
        print(f"Test result saved to {output_file}")
    else:
        # logger.warning(f"Test file not found: {test_file}")
        print(f"Test file not found: {test_file}")
        
    # Process all PDFs in uploads directory
    # logger.info("Processing all PDFs in uploads directory")
    results = extractor.batch_process(UPLOADS_DIR, sample_jd, anonymize=True)
    
    # logger.info(f"Processed {len(results)} PDF files")
    print(f"Processed {len(results)} PDF files")
    
if __name__ == "__main__":
    main()
