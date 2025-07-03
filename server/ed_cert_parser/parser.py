#!/usr/bin/env python3
"""
Certificate Processor - Single File Solution
Extracts information from PDF certificates including university certificates and online course certificates.
"""

import os
import re
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging

# Third-party imports
try:
    import pdfplumber
    import pytesseract
    import easyocr
    import cv2
    import numpy as np
    from PIL import Image
    import spacy
    import dateparser
    import requests
    from pyzbar import pyzbar
    import qrcode
    from urllib.parse import urlparse
    import hashlib
    import base64
except ImportError as e:
    print(f"Missing required package: {e.name}")
    print("Please install required packages:")
    print("pip install pdfplumber pytesseract easyocr opencv-python pillow spacy dateparser requests pyzbar qrcode urllib3")
    print("python -m spacy download en_core_web_sm")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CertificateProcessor:
    """Main class for processing PDF certificates and extracting structured data."""
    
    def __init__(self, upload_folder="upload", output_folder="output"):
        self.upload_folder = Path(upload_folder)
        self.output_folder = Path(output_folder)
        
        # Create folders if they don't exist
        self.upload_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)
        
        # Initialize OCR engines
        self.tesseract_config = "--oem 3 --psm 6"
        try:
            self.easyocr_reader = easyocr.Reader(["en"], gpu=False)
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self.easyocr_reader = None
        
        # Initialize spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Define extraction patterns
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize regex patterns for extracting certificate information."""
        
        # University/Institution patterns
        self.university_patterns = [
            # Course completion and online providers
            r'(?:authorized by|offered by|in partnership with)\s+([A-Za-z\s,.-]+?)(?:\s+and offered through|\s+through|$|\n)',
            r'([A-Za-z\s,.-]+?)\s+(?:and offered through Coursera|via edX|on Udacity)(?:\s|$|,|\n)',
            r'(?:Meta|Google|IBM|Microsoft|Amazon|Facebook|Apple|Netflix|Tesla)\s*([A-Za-z\s,.-]*?)(?:\s|$|,|\n)',
            
            # Traditional university patterns
            r'(?:University of|at|from)\s+([A-Za-z\s,.-]+?)(?:\s|$|,|\n)',
            r'([A-Za-z\s,.-]+?)\s+University(?:\s|$|,|\n)',
            r'([A-Za-z\s,.-]+?)\s+College(?:\s|$|,|\n)',
            r'([A-Za-z\s,.-]+?)\s+Institute(?:\s|$|,|\n)',
            
            # International universities
            r'([A-Za-z\s,.-]+?)\s+(?:Universität|Universidad|Université|Università)(?:\s|$|,|\n)',
            
            # Technical institutes
            r'(?:IIT|MIT|ITT|NIT)\s+([A-Za-z\s,.-]+?)(?:\s|$|,|\n)',
            r'([A-Za-z\s,.-]+?)\s+(?:Institute of Technology|Technical University)(?:\s|$|,|\n)',
        ]
        
        # Degree/Course patterns
        self.degree_patterns = [
            # Course completion patterns (prioritized for online courses)
            r'(?:has successfully completed|completed)\s+([A-Za-z\s,.-]+?)(?:\s+an online|\s+course|\s+program|$|\n)',
            r'(?:Certificate of Completion for|Certification in)\s+([A-Za-z\s,.-]+?)(?:\s|$|,|\n)',
            
            # Traditional degrees
            r'Bachelor\s+of\s+([A-Za-z\s,.-]+?)(?:\s|$|,|\n|\()',
            r'Master\s+of\s+([A-Za-z\s,.-]+?)(?:\s|$|,|\n|\()',
            r'Doctor\s+of\s+([A-Za-z\s,.-]+?)(?:\s|$|,|\n|\()',
            r'Ph\.?D\.?\s*(?:in\s+)?([A-Za-z\s,.-]+?)(?:\s|$|,|\n|\()',
            
            # Diplomas and Certificates
            r'Diploma\s+(?:in\s+)?([A-Za-z\s,.-]+?)(?:\s|$|,|\n|\()',
            r'Certificate\s+(?:in\s+)?([A-Za-z\s,.-]+?)(?:\s|$|,|\n|\()',
            
            # Online course patterns
            r'(?:Introduction to|Fundamentals of|Advanced|Complete|Professional)\s+([A-Za-z\s,.-]+?)(?:\s+Development|\s+Programming|\s+Course|\s+Certification|$|\n)',
            r'([A-Za-z\s,.-]+?)\s+(?:Development|Programming|Course|Certification|Specialization)(?:\s|$|,|\n)',
        ]
        
        # GPA patterns
        self.gpa_patterns = [
            r'(?:GPA|Grade Point Average)[:\s]+(\d+\.?\d*)\s*(?:/\s*(\d+\.?\d*))?',
            r'(?:CGPA|Cumulative GPA)[:\s]+(\d+\.?\d*)\s*(?:/\s*(\d+\.?\d*))?',
            r'(?:Percentage|Percent|%)[:\s]*(\d+\.?\d*)\s*%?',
        ]
        
        # Date patterns
        self.date_patterns = [
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}',
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'(?:Conferred|Granted|Awarded|Issued).*?(\d{4})',
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber and OCR fallback."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    # Try direct text extraction first
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 0:
                        text += page_text + "\n"
                    else:
                        # Fallback to OCR if direct extraction fails
                        try:
                            img = page.to_image().original
                            img = np.array(img)
                            img = self._preprocess_image(img)
                            ocr_text = self._extract_text_with_ocr(img)
                            text += ocr_text + "\n"
                        except Exception as ocr_error:
                            logger.warning(f"OCR failed for page: {ocr_error}")
                
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            return thresh
        except Exception:
            return image
    
    def _extract_text_with_ocr(self, image: np.ndarray) -> str:
        """Extract text using OCR engines."""
        text = ""
        
        # Try Tesseract first
        try:
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
        except Exception as e:
            logger.warning(f"Tesseract OCR failed: {e}")
        
        # Fallback to EasyOCR if Tesseract fails or produces no text
        if not text.strip() and self.easyocr_reader:
            try:
                result = self.easyocr_reader.readtext(image)
                text = " ".join([res[1] for res in result])
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}")
        
        return text.strip()
    
    def detect_qr_codes(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect and decode QR codes in the image."""
        qr_codes = []
        try:
            decoded_objects = pyzbar.decode(image)
            for obj in decoded_objects:
                qr_data = {
                    "type": obj.type,
                    "data": obj.data.decode('utf-8'),
                    "rect": obj.rect,
                    "polygon": obj.polygon
                }
                qr_codes.append(qr_data)
                logger.info(f"QR Code detected: {qr_data['data']}")
        except Exception as e:
            logger.warning(f"QR code detection failed: {e}")
        
        return qr_codes
    
    def verify_qr_code_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Verify QR code URL by making HTTP request."""
        verification_result = {
            "url": url,
            "accessible": False,
            "status_code": None,
            "content_type": None,
            "title": None,
            "error": None
        }
        
        try:
            # Parse URL to ensure it's valid
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                verification_result["error"] = "Invalid URL format"
                return verification_result
            
            # Make HTTP request with timeout
            headers = {
                'User-Agent': 'Certificate-Processor/1.0 (Verification Bot)'
            }
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            verification_result["accessible"] = True
            verification_result["status_code"] = response.status_code
            verification_result["content_type"] = response.headers.get('Content-Type', '')
            
            # Try to extract title from HTML response
            if 'text/html' in verification_result["content_type"]:
                import re
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                if title_match:
                    verification_result["title"] = title_match.group(1).strip()
            
            logger.info(f"QR URL verified: {url} - Status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            verification_result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError:
            verification_result["error"] = "Connection error"
        except Exception as e:
            verification_result["error"] = str(e)
        
        return verification_result
    
    def detect_digital_signatures(self, pdf_path: str) -> Dict[str, Any]:
        """Detect digital signatures and security features in PDF."""
        signature_info = {
            "has_digital_signature": False,
            "signature_count": 0,
            "security_features": [],
            "metadata": {},
            "encrypted": False,
            "error": None
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Check PDF metadata
                if pdf.metadata:
                    signature_info["metadata"] = {
                        "creator": pdf.metadata.get("Creator", ""),
                        "producer": pdf.metadata.get("Producer", ""),
                        "subject": pdf.metadata.get("Subject", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "creation_date": str(pdf.metadata.get("CreationDate", "")),
                        "modification_date": str(pdf.metadata.get("ModDate", ""))
                    }
                
                # Check if PDF is encrypted
                signature_info["encrypted"] = getattr(pdf.stream, 'isEncrypted', False)
                
                # Look for common security indicators in metadata
                producer = signature_info["metadata"].get("producer", "").lower()
                creator = signature_info["metadata"].get("creator", "").lower()
                
                security_keywords = [
                    "adobe acrobat", "docusign", "adobe sign", "hellosign", 
                    "pandadoc", "signrequest", "eversign", "signnow"
                ]
                
                for keyword in security_keywords:
                    if keyword in producer or keyword in creator:
                        signature_info["security_features"].append(f"Signed with {keyword}")
                
                # Check for form fields (often used in digital signatures)
                for page in pdf.pages:
                    if hasattr(page, 'annots') and page.annots:
                        signature_info["security_features"].append("Contains form annotations")
                        break
                
                logger.info(f"Digital signature analysis completed for {pdf_path}")
                
        except Exception as e:
            signature_info["error"] = str(e)
            logger.warning(f"Digital signature detection failed: {e}")
        
        return signature_info
    
    def calculate_document_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of the document for integrity verification."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Hash calculation failed: {e}")
            return ""
    
    def validate_certificate_authenticity(self, pdf_path: str, extracted_text: str) -> Dict[str, Any]:
        """Comprehensive authenticity validation."""
        authenticity_report = {
            "overall_score": 0.0,
            "qr_codes": [],
            "qr_verification": [],
            "digital_signatures": {},
            "document_hash": "",
            "authenticity_indicators": [],
            "risk_factors": [],
            "recommendations": []
        }
        
        try:
            # Calculate document hash
            authenticity_report["document_hash"] = self.calculate_document_hash(pdf_path)
            
            # Check for digital signatures
            authenticity_report["digital_signatures"] = self.detect_digital_signatures(pdf_path)
            
            # Process PDF pages to look for QR codes
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Convert page to image for QR detection
                        img = page.to_image().original
                        img_array = np.array(img)
                        
                        # Detect QR codes
                        qr_codes = self.detect_qr_codes(img_array)
                        if qr_codes:
                            authenticity_report["qr_codes"].extend(qr_codes)
                            
                            # Verify QR code URLs
                            for qr in qr_codes:
                                if qr["data"].startswith(("http://", "https://")):
                                    verification = self.verify_qr_code_url(qr["data"])
                                    authenticity_report["qr_verification"].append(verification)
                    
                    except Exception as e:
                        logger.warning(f"QR code detection failed for page {page_num}: {e}")
            
            # Analyze authenticity indicators
            score = 0.0
            
            # QR code verification
            if authenticity_report["qr_codes"]:
                authenticity_report["authenticity_indicators"].append("Contains QR codes for verification")
                score += 25
                
                verified_qr = sum(1 for qr in authenticity_report["qr_verification"] 
                                if qr.get("accessible") and qr.get("status_code") == 200)
                if verified_qr > 0:
                    authenticity_report["authenticity_indicators"].append(f"{verified_qr} QR code(s) successfully verified")
                    score += 25
                else:
                    authenticity_report["risk_factors"].append("QR codes present but not accessible")
            
            # Digital signature analysis
            if authenticity_report["digital_signatures"].get("security_features"):
                authenticity_report["authenticity_indicators"].extend(
                    authenticity_report["digital_signatures"]["security_features"]
                )
                score += 20
            
            # Metadata analysis
            metadata = authenticity_report["digital_signatures"].get("metadata", {})
            if metadata.get("creator") or metadata.get("producer"):
                authenticity_report["authenticity_indicators"].append("Contains creation metadata")
                score += 10
            
            # Text-based indicators
            verification_keywords = [
                "verify", "verification", "authenticate", "digital", "certificate id",
                "verification code", "license number", "registration number"
            ]
            
            text_lower = extracted_text.lower()
            found_keywords = [kw for kw in verification_keywords if kw in text_lower]
            if found_keywords:
                authenticity_report["authenticity_indicators"].append(
                    f"Contains verification keywords: {', '.join(found_keywords)}"
                )
                score += len(found_keywords) * 2
            
            # Institution credibility check
            known_institutions = [
                "university", "college", "institute", "coursera", "edx", "udacity",
                "meta", "google", "microsoft", "ibm", "amazon", "adobe"
            ]
            
            found_institutions = [inst for inst in known_institutions if inst in text_lower]
            if found_institutions:
                authenticity_report["authenticity_indicators"].append(
                    f"Issued by recognized institutions: {', '.join(found_institutions)}"
                )
                score += 10
            
            # Risk factors
            if not authenticity_report["qr_codes"] and not authenticity_report["digital_signatures"]["security_features"]:
                authenticity_report["risk_factors"].append("No digital verification methods detected")
            
            if not metadata.get("creator") and not metadata.get("producer"):
                authenticity_report["risk_factors"].append("Missing creation metadata")
            
            # Calculate overall score (max 100)
            authenticity_report["overall_score"] = min(score, 100.0)
            
            # Generate recommendations
            if authenticity_report["overall_score"] >= 80:
                authenticity_report["recommendations"].append("High authenticity confidence - certificate appears genuine")
            elif authenticity_report["overall_score"] >= 60:
                authenticity_report["recommendations"].append("Moderate authenticity confidence - verify through additional means")
            elif authenticity_report["overall_score"] >= 40:
                authenticity_report["recommendations"].append("Low authenticity confidence - manual verification recommended")
            else:
                authenticity_report["recommendations"].append("Very low authenticity confidence - exercise caution")
            
            if authenticity_report["qr_verification"]:
                for qr in authenticity_report["qr_verification"]:
                    if qr.get("accessible"):
                        authenticity_report["recommendations"].append(f"Verify certificate at: {qr['url']}")
            
        except Exception as e:
            authenticity_report["error"] = str(e)
            logger.error(f"Authenticity validation failed: {e}")
        
        return authenticity_report
    
    def extract_entities_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy NLP."""
        entities = {"universities": [], "organizations": [], "persons": []}
        
        if not self.nlp:
            return entities
        
        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG"]:
                    # Check if it looks like a university
                    if any(word in ent.text.lower() for word in ["university", "college", "institute", "school"]):
                        entities["universities"].append(ent.text)
                    else:
                        entities["organizations"].append(ent.text)
                elif ent.label_ == "PERSON":
                    entities["persons"].append(ent.text)
        except Exception as e:
            logger.warning(f"spaCy processing failed: {e}")
        
        return entities
    
    def extract_certificate_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from certificate text."""
        result = {
            "university": None,
            "degree": None,
            "gpa": None,
            "graduation_date": None,
            "confidence_scores": {"university": 0.0, "degree": 0.0, "gpa": 0.0, "graduation_date": 0.0},
            "extraction_methods": {"university": "none", "degree": "none", "gpa": "none", "graduation_date": "none"},
            "raw_matches": {"university": [], "degree": [], "gpa": [], "graduation_date": []},
            "extracted_entities": {}
        }
        
        # Extract entities using spaCy
        result["extracted_entities"] = self.extract_entities_with_spacy(text)
        
        # Extract university/institution
        university_matches = []
        for pattern in self.university_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            university_matches.extend(matches)
        
        result["raw_matches"]["university"] = university_matches
        
        if university_matches:
            # Filter and choose the best match
            filtered_matches = [match.strip() for match in university_matches if len(match.strip()) > 2]
            if filtered_matches:
                # Prefer specific company/institution names over generic text
                priority_matches = [m for m in filtered_matches if m in ["Meta", "Google", "IBM", "Microsoft", "Amazon", "Facebook", "Apple"]]
                if priority_matches:
                    best_match = priority_matches[0]
                else:
                    # Prefer shorter, cleaner matches for university names
                    best_match = min(filtered_matches, key=len).strip()
                    # Clean up common issues
                    if "\n" in best_match:
                        lines = best_match.split("\n")
                        best_match = max(lines, key=len).strip()
                result["university"] = best_match
                result["confidence_scores"]["university"] = 0.8 if len(best_match) > 3 else 0.6
                result["extraction_methods"]["university"] = "regex"
        elif result["extracted_entities"]["universities"]:
            # Fallback to spaCy entities
            result["university"] = result["extracted_entities"]["universities"][0]
            result["confidence_scores"]["university"] = 0.7
            result["extraction_methods"]["university"] = "spacy"
        elif result["extracted_entities"]["organizations"]:
            # Use organization entities as fallback
            result["university"] = result["extracted_entities"]["organizations"][0]
            result["confidence_scores"]["university"] = 0.5
            result["extraction_methods"]["university"] = "spacy_org"
        
        # Extract degree/course
        degree_matches = []
        for pattern in self.degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            degree_matches.extend(matches)
        
        result["raw_matches"]["degree"] = degree_matches
        
        if degree_matches:
            # Filter and choose the best match
            filtered_matches = [match.strip() for match in degree_matches if len(match.strip()) > 3]
            if filtered_matches:
                # Prefer full course names over partial matches
                course_matches = [m for m in filtered_matches if any(word in m.lower() for word in ["introduction", "development", "science", "engineering", "certificate", "diploma", "bachelor", "master"])]
                if course_matches:
                    # Choose the one that contains "Introduction to" or similar course indicators
                    intro_matches = [m for m in course_matches if "introduction" in m.lower()]
                    if intro_matches:
                        best_match = max(intro_matches, key=len).strip()
                    else:
                        best_match = max(course_matches, key=len).strip()
                else:
                    best_match = max(filtered_matches, key=len).strip()
                    
                # Clean up common issues
                if "\n" in best_match:
                    lines = best_match.split("\n")
                    best_match = max(lines, key=len).strip()
                result["degree"] = best_match
                result["confidence_scores"]["degree"] = 0.8 if len(best_match) > 10 else 0.6
                result["extraction_methods"]["degree"] = "regex"
        
        # Extract GPA
        gpa_matches = []
        for pattern in self.gpa_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            gpa_matches.extend([match[0] if isinstance(match, tuple) else match for match in matches])
        
        result["raw_matches"]["gpa"] = gpa_matches
        
        if gpa_matches:
            try:
                gpa_value = float(gpa_matches[0])
                result["gpa"] = f"{gpa_value:.2f}"
                result["confidence_scores"]["gpa"] = 0.9
                result["extraction_methods"]["gpa"] = "regex"
            except ValueError:
                pass
        
        # Extract graduation date
        date_matches = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            date_matches.extend(matches)
        
        # Also look for simple date patterns
        simple_dates = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}', text, re.IGNORECASE)
        date_matches.extend(simple_dates)
        
        result["raw_matches"]["graduation_date"] = date_matches
        
        if date_matches:
            # Try to parse the date
            best_date = None
            for date_str in date_matches:
                try:
                    parsed_date = dateparser.parse(str(date_str))
                    if parsed_date:
                        best_date = parsed_date.strftime("%B %Y")
                        break
                except Exception:
                    continue
            
            if best_date:
                result["graduation_date"] = best_date
                result["confidence_scores"]["graduation_date"] = 0.8
                result["extraction_methods"]["graduation_date"] = "dateparser"
            else:
                # Use the first date match as is
                result["graduation_date"] = str(date_matches[0]).strip()
                result["confidence_scores"]["graduation_date"] = 0.6
                result["extraction_methods"]["graduation_date"] = "regex"
        
        # Calculate overall confidence
        scores = list(result["confidence_scores"].values())
        result["confidence_scores"]["overall"] = sum(scores) / len(scores)
        
        return result
    
    def process_file(self, filename: str) -> Dict[str, Any]:
        """Process a single PDF file and return extracted information."""
        file_path = self.upload_folder / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() == '.pdf':
            raise ValueError("Only PDF files are supported")
        
        logger.info(f"Processing file: {filename}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(str(file_path))
        
        # Extract certificate information
        cert_info = self.extract_certificate_info(text)
        
        # Perform authenticity validation
        logger.info(f"Validating authenticity for: {filename}")
        authenticity = self.validate_certificate_authenticity(str(file_path), text)
        cert_info["authenticity"] = authenticity
        
        # Add metadata
        cert_info["source_file"] = filename
        cert_info["processed_at"] = datetime.now().isoformat()
        cert_info["text_length"] = len(text)
        
        # Save results to output folder
        output_filename = f"{file_path.stem}_extracted.json"
        output_path = self.output_folder / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cert_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_path}")
        logger.info(f"Authenticity score: {authenticity.get('overall_score', 0):.1f}/100")
        
        return cert_info
    
    def process_all_files(self) -> List[Dict[str, Any]]:
        """Process all PDF files in the upload folder."""
        results = []
        pdf_files = list(self.upload_folder.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.upload_folder}")
            return results
        
        for pdf_file in pdf_files:
            try:
                result = self.process_file(pdf_file.name)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
        
        logger.info(f"Processing complete. Processed {len(results)} files successfully.")
        
        return results

def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(description="Certificate Processor - Extract information from PDF certificates")
    parser.add_argument("--file", type=str, help="Process a specific file")
    parser.add_argument("--all", action="store_true", help="Process all files in upload folder")
    parser.add_argument("--upload-folder", type=str, default="upload", help="Upload folder path")
    parser.add_argument("--output-folder", type=str, default="output", help="Output folder path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize processor
    processor = CertificateProcessor(args.upload_folder, args.output_folder)
    
    try:
        if args.file:
            # Process single file
            result = processor.process_file(args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.all:
            # Process all files
            results = processor.process_all_files()
            print(f"Processed {len(results)} files.")
            print("Check the output folder for detailed results.")
        
        else:
            # Interactive mode
            print("Certificate Processor - Interactive Mode")
            print("Commands:")
            print("  file <filename>  - Process a specific file")
            print("  all              - Process all files in upload folder")
            print("  quit             - Exit")
            
            while True:
                try:
                    command = input("\n> ").strip().split()
                    if not command:
                        continue
                    
                    if command[0] == "quit":
                        break
                    elif command[0] == "file" and len(command) > 1:
                        result = processor.process_file(command[1])
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                    elif command[0] == "all":
                        results = processor.process_all_files()
                        print(f"Processed {len(results)} files.")
                    else:
                        print("Invalid command. Use 'file <filename>', 'all', or 'quit'")
                
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
