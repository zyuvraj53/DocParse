import pdfplumber
import docx
import pytesseract
from PIL import Image
import re
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import dateparser
    HAS_DATEPARSER = True
except ImportError:
    HAS_DATEPARSER = False
    logger.warning("dateparser not available, using basic date parsing")

try:
    from fuzzywuzzy import fuzz, process
    HAS_FUZZYWUZZY = True
except ImportError:
    HAS_FUZZYWUZZY = False
    logger.warning("fuzzywuzzy not available, using exact matching")

# Check for Tesseract installation and configure
def check_tesseract_installation():
    """Check if Tesseract is available and try to configure it."""
    try:
        # Try default pytesseract
        pytesseract.image_to_string(Image.new('RGB', (100, 30), color='white'))
        return True
    except Exception as e:
        if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
            # Common Windows installation paths
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Tesseract-OCR\tesseract.exe',
                r'C:\Tools\Tesseract-OCR\tesseract.exe'
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Found Tesseract at: {path}")
                    try:
                        pytesseract.image_to_string(Image.new('RGB', (100, 30), color='white'))
                        return True
                    except:
                        continue
                        
            logger.warning("Tesseract OCR not found in common locations.")
            logger.warning("Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
            logger.warning("Or set pytesseract.pytesseract.tesseract_cmd to the correct path")
            return False
        else:
            logger.warning(f"Tesseract test failed: {e}")
            return False

# Check Tesseract on startup
TESSERACT_AVAILABLE = check_tesseract_installation()

def extract_text_from_pdf(file_path):
    """Extract text from PDF files using pdfplumber with OCR fallback."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If no text was extracted, try OCR on the PDF pages
            if not text.strip():
                if not TESSERACT_AVAILABLE:
                    logger.error(f"No selectable text in {file_path} and OCR not available")
                    return None
                    
                logger.info(f"No selectable text found in {file_path}, attempting OCR...")
                try:
                    from PIL import Image
                    import io
                    
                    with pdfplumber.open(file_path) as pdf:
                        for page_num, page in enumerate(pdf.pages):
                            # Convert PDF page to image
                            page_image = page.within_bbox(page.bbox).to_image(resolution=300)
                            
                            # Convert to PIL Image and apply OCR
                            pil_image = page_image.original
                            page_text = pytesseract.image_to_string(pil_image, config='--oem 3 --psm 6')
                            
                            if page_text.strip():
                                text += page_text + "\n"
                                logger.info(f"OCR extracted {len(page_text)} characters from page {page_num + 1}")
                
                except Exception as ocr_error:
                    if "tesseract is not installed" in str(ocr_error).lower() or "not found" in str(ocr_error).lower():
                        logger.error(f"Tesseract OCR not found. Please install Tesseract:")
                        logger.error("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
                        logger.error("After installation, add Tesseract to your PATH or set TESSDATA_PREFIX")
                    else:
                        logger.warning(f"OCR failed for {file_path}: {ocr_error}")
            
            return text.strip() if text.strip() else None
            
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return None

def extract_text_from_docx(file_path):
    """Extract text from DOCX files using python-docx."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip()
    except Exception as e:
        logger.error(f"Error reading DOCX {file_path}: {e}")
        return None

def extract_text_from_doc(file_path):
    """Extract text from DOC files - fallback to OCR."""
    try:
        # For .doc files, try docx first then fallback to OCR
        return extract_text_from_docx(file_path)
    except Exception as e:
        logger.warning(f"DOC format {file_path} not supported directly, trying OCR: {e}")
        return extract_text_from_image(file_path)

def extract_text_from_image(file_path):
    """Extract text from images using pytesseract."""
    if not TESSERACT_AVAILABLE:
        logger.error(f"OCR not available for image {file_path}")
        return None
        
    try:
        # Configure pytesseract for better accuracy
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(Image.open(file_path), config=custom_config)
        return text.strip()
    except Exception as e:
        logger.error(f"Error reading image {file_path}: {e}")
        return None

def clean_text(text):
    """Clean and normalize text for better parsing."""
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    # Fix common OCR errors
    text = text.replace('|', 'I').replace('0', 'O') if text.startswith('0') else text
    # Normalize quotes and special characters
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    return text.strip()

def extract_dates_from_text(text):
    """Extract all possible dates from text using multiple patterns."""
    dates_found = []
    
    # Multiple date patterns for different formats
    date_patterns = [
        r'\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})\b',  # DD/MM/YYYY or MM/DD/YYYY
        r'\b(\d{4})[\/\-.](\d{1,2})[\/\-.](\d{1,2})\b',  # YYYY/MM/DD
        r'\b([A-Za-z]{3,12})\s+(\d{1,2}),?\s+(\d{4})\b',  # Month DD, YYYY
        r'\b(\d{1,2})\s+([A-Za-z]{3,12})\s+(\d{4})\b',    # DD Month YYYY
        r'\b([A-Za-z]{3,12})\s+(\d{4})\b',                # Month YYYY
        r'\b(\d{1,2})[a-z]{2}\s+([A-Za-z]{3,12})\s+(\d{4})\b',  # 1st January 2020
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(0)
            # Use dateparser if available, otherwise fallback parsing
            parsed_date = None
            
            if HAS_DATEPARSER:
                try:
                    import dateparser
                    parsed_date = dateparser.parse(date_str)
                except:
                    pass
            
            if not parsed_date:
                # Fallback manual date parsing
                date_formats = [
                    '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', 
                    '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d',
                    '%B %d, %Y', '%d %B %Y', '%B %Y',
                    '%b %d, %Y', '%d %b %Y', '%b %Y'
                ]
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            if parsed_date:
                # Determine the context of this date
                context_before = text[max(0, match.start()-50):match.start()].lower()
                context_after = text[match.start():min(len(text), match.end()+50)].lower()
                
                date_type = 'unknown'
                
                # Skip document dates (at the beginning)
                if match.start() < 100 and ('date:' in context_before or match.start() < 50):
                    date_type = 'document_date'
                # Look for employment start indicators
                elif any(keyword in context_before + context_after for keyword in 
                        ['from', 'since', 'joined', 'started', 'employed from', 'worked from']):
                    date_type = 'start_date'
                # Look for employment end indicators  
                elif any(keyword in context_before + context_after for keyword in 
                        ['to', 'until', 'till', 'ended', 'left', 'relieved']):
                    date_type = 'end_date'
                
                dates_found.append({
                    'raw': date_str,
                    'parsed': parsed_date,
                    'position': match.start(),
                    'type': date_type,
                    'context': context_before + " [DATE] " + context_after
                })
    
    # Sort by position in text
    dates_found.sort(key=lambda x: x['position'])
    return dates_found

def extract_organization_name(text):
    """Extract organization name using multiple strategies."""
    patterns = [
        # Standard patterns
        r'employed\s+(?:with|at|by)\s+([A-Za-z][A-Za-z\s&.,()0-9]+?)(?:\s+(?:as|from|since|during))',
        r'working\s+(?:with|at|for)\s+([A-Za-z][A-Za-z\s&.,()0-9]+?)(?:\s+(?:as|from|since))',
        r'(?:company|organization|employer)[\s:]+([A-Za-z][A-Za-z\s&.,()0-9]+?)(?:\s+(?:as|from|\.|\n))',
        r'([A-Za-z][A-Za-z\s&.,()0-9]+?)\s+(?:pvt\.?\s*ltd\.?|ltd\.?|inc\.?|corp\.?|llc|limited)',
        
        # Template-specific patterns
        r'(?:^|\n)([A-Z][A-Za-z\s&.,()0-9]+?)\s*\n.*(?:experience|employment|letter)',
        r'letterhead[:\s]*([A-Za-z][A-Za-z\s&.,()0-9]+)',
        r'from[:\s]*([A-Za-z][A-Za-z\s&.,()0-9]+?)(?:\s+(?:to|regarding))',
        
        # More flexible patterns
        r'certify\s+that\s+[A-Za-z\s]+\s+(?:was\s+)?(?:employed|worked|served)\s+(?:with|at|for|by)\s+([A-Za-z][A-Za-z\s&.,()0-9]+?)(?:\s+(?:as|from))',
        r'(?:this\s+)?(?:is\s+to\s+)?(?:certify|confirm)\s+that\s+[A-Za-z\s]+\s+(?:was\s+)?(?:employed|worked)\s+(?:with|at)\s+([A-Za-z][A-Za-z\s&.,()0-9]+)',
        
        # Header patterns for templates
        r'^([A-Z][A-Za-z\s&.,()0-9]{5,50})\s*$',  # Company name as header
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            org_name = match.group(1).strip()
            # Clean up common artifacts
            org_name = re.sub(r'\s+', ' ', org_name)
            org_name = re.sub(r'[^\w\s&.,()-]', '', org_name)
            
            # Skip if it's too short, too long, or contains template words
            if (len(org_name) > 3 and len(org_name) < 100 and 
                not any(word in org_name.lower() for word in ['template', 'sample', 'example', 'experience', 'letter'])):
                return org_name
    
    return None

def extract_job_title(text):
    """Extract job title using patterns and fuzzy matching."""
    common_titles = [
        'software engineer', 'developer', 'analyst', 'manager', 'director', 
        'consultant', 'specialist', 'executive', 'coordinator', 'administrator',
        'qa engineer', 'tester', 'project manager', 'team lead', 'architect',
        'designer', 'marketing manager', 'sales executive', 'hr manager', 
        'finance manager', 'accountant', 'data scientist', 'business analyst',
        'qa analyst', 'quality analyst', 'test engineer', 'senior developer',
        'marketing executive', 'software developer', 'senior analyst',
        'operations engineer', 'academic counselor', 'system administrator'
    ]
    
    patterns = [
        # Most specific patterns first
        r'employed\s+with\s+[A-Za-z\s&.,()0-9]+?\s+as\s+(?:a\s+)?([A-Za-z][A-Za-z\s\-/&]+?)(?:\s+from)',
        r'employed\s+[A-Za-z\s&.,()0-9]+?\s+as\s+(?:a\s+)?([A-Za-z][A-Za-z\s\-/&]+?)(?:\s+from)',
        r'working\s+as\s+(?:a\s+)?([A-Za-z][A-Za-z\s\-/&]+?)(?:\s+(?:with|at|from))',
        r'(?:as|position|title|designation|role)[\s:]+(?:a\s+)?([A-Za-z][A-Za-z\s\-/&]+?)(?:\s+(?:from|with|at|during|\.|,))',
        r'position\s+of\s+([A-Za-z][A-Za-z\s\-/&]+?)(?:\s+(?:from|with|at))',
        r'(?:served|worked)\s+as\s+(?:a\s+)?([A-Za-z][A-Za-z\s\-/&]+?)(?:\s+(?:from|with|at))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            title = re.sub(r'\s+', ' ', title)
            
            # Clean up common artifacts
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Use fuzzy matching if available
            if HAS_FUZZYWUZZY:
                try:
                    from fuzzywuzzy import process
                    best_match = process.extractOne(title.lower(), common_titles)
                    if best_match and best_match[1] > 70:  # 70% similarity threshold
                        return best_match[0].title()
                except:
                    pass
            
            # Simple matching fallback
            title_lower = title.lower()
            
            # First try exact match
            for common_title in common_titles:
                if common_title.lower() == title_lower:
                    return common_title.title()
            
            # Then try partial match only if no exact match found
            for common_title in common_titles:
                if common_title.lower() in title_lower and len(common_title) > 3:
                    # Only use partial match if it's a significant portion
                    if len(common_title) / len(title) > 0.7:
                        return common_title.title()
            
            # Return the extracted title if it's reasonable and not a generic word
            if len(title) > 2 and len(title) < 50 and not title.lower() in ['employed', 'working', 'position', 'job']:
                return title.title()
    
    return None

def extract_employee_name(text):
    """Extract employee name from the letter with enhanced patterns."""
    patterns = [
        # Standard patterns
        r'(?:that|certify that|mr\.?\s*|ms\.?\s*|mrs\.?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'employee[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:name|person)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+was\s+employed|\s+worked|\s+has\s+been)',
        
        # Template-specific patterns
        r'employee\s+name[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'name\s+of\s+employee[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:mr|ms|mrs)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:was|is|has)',
        
        # More flexible patterns
        r'(?:to\s+whom\s+it\s+may\s+concern.*?)([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:was|is|has))',
        r'(?:this\s+is\s+to\s+certify.*?)([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+(?:was|is|has))',
        
        # Fallback: Look for capitalized names near employment keywords
        r'(?:employ|work|serv)(?:ed|ing).*?([A-Z][a-z]+\s+[A-Z][a-z]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            name = match.group(1).strip()
            # Check if it's a valid name (at least 2 words, not too long, not common words)
            name_parts = name.split()
            if (len(name_parts) >= 2 and len(name) < 50 and 
                not any(word.lower() in ['company', 'organization', 'employee', 'name', 'template', 'sample'] 
                       for word in name_parts)):
                return name
    
    return None

def extract_manager_info(text):
    """Extract manager information if present."""
    manager_info = {
        'manager_name': None,
        'manager_title': None,
        'manager_contact': None
    }
    
    # Manager name patterns
    name_patterns = [
        r'(?:manager|supervisor|reporting\s+to|signed\s+by|approved\s+by)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:hr\s+manager|human\s+resources)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            manager_info['manager_name'] = match.group(1).strip()
            break
    
    # Manager contact (email/phone)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        manager_info['manager_contact'] = email_match.group(0)
    
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', text)
    if phone_match and not email_match:
        manager_info['manager_contact'] = phone_match.group(0).strip()
    
    return manager_info

def parse_letter(text):
    """Parse experience letter text to extract details and check consistency."""
    if not text:
        return {"error": "No text extracted from the document"}

    # Clean the text first
    cleaned_text = clean_text(text)
    
    result = {
        "extracted_data": {},
        "formatting_consistency": {},
        "anomalies": [],
        "confidence_score": 0.0
    }

    try:
        # Extract all information using the new robust functions
        dates = extract_dates_from_text(cleaned_text)
        org_name = extract_organization_name(cleaned_text)
        job_title = extract_job_title(cleaned_text)
        employee_name = extract_employee_name(cleaned_text)
        manager_info = extract_manager_info(cleaned_text)
        
        # Determine start and end dates with better logic
        start_date = None
        end_date = None
        duration_years = None
        
        # Filter out document dates and find employment dates
        employment_dates = [d for d in dates if d['type'] != 'document_date']
        
        if len(employment_dates) >= 2:
            # Look for explicit start and end dates
            start_dates = [d for d in employment_dates if d['type'] == 'start_date']
            end_dates = [d for d in employment_dates if d['type'] == 'end_date']
            
            if start_dates and end_dates:
                start_date = start_dates[0]['parsed'].strftime('%Y-%m-%d')
                end_date = end_dates[0]['parsed'].strftime('%Y-%m-%d')
            else:
                # Fallback: use chronological order, but look for "from X to Y" patterns
                from_to_pattern = r'from\s+([A-Za-z0-9\s,/.-]+?)\s+to\s+([A-Za-z0-9\s,/.-]+)'
                from_to_match = re.search(from_to_pattern, cleaned_text, re.IGNORECASE)
                
                if from_to_match and len(employment_dates) >= 2:
                    # Sort by date value, not position
                    employment_dates.sort(key=lambda x: x['parsed'])
                    start_date = employment_dates[0]['parsed'].strftime('%Y-%m-%d')
                    end_date = employment_dates[-1]['parsed'].strftime('%Y-%m-%d')
                
        elif len(employment_dates) == 1:
            # Try to find duration mentioned in text
            duration_match = re.search(r'(\d+(?:\.\d+)?)\s*years?', cleaned_text, re.IGNORECASE)
            if duration_match:
                duration_years = float(duration_match.group(1))
                # If we have one date and duration, we can infer the other date
                single_date = employment_dates[0]['parsed']
                if employment_dates[0]['type'] == 'start_date' or re.search(r'from.*to|since.*until', cleaned_text, re.IGNORECASE):
                    start_date = single_date.strftime('%Y-%m-%d')
                else:
                    end_date = single_date.strftime('%Y-%m-%d')
        
        # Calculate duration if we have both dates
        if start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                delta = end_dt - start_dt
                duration_years = round(delta.days / 365.25, 2)
            except ValueError:
                pass
        
        # Populate extracted data
        if org_name:
            result["extracted_data"]["org_name"] = org_name
        if job_title:
            result["extracted_data"]["job_title"] = job_title
        if employee_name:
            result["extracted_data"]["employee_name"] = employee_name
        if start_date:
            result["extracted_data"]["start_date"] = start_date
        if end_date:
            result["extracted_data"]["end_date"] = end_date
        if duration_years:
            result["extracted_data"]["duration_years"] = duration_years
        
        # Add manager info if available
        for key, value in manager_info.items():
            if value:
                result["extracted_data"][key] = value
        
        # Validate consistency and detect anomalies
        consistency, anomalies = validate_extracted_data(result["extracted_data"], cleaned_text)
        result["formatting_consistency"] = consistency
        result["anomalies"].extend(anomalies)
        
        # Calculate confidence score based on fields found
        required_fields = ["org_name", "job_title", "employee_name", "start_date", "end_date"]
        optional_fields = ["duration_years", "manager_name", "manager_contact"]
        
        found_required = sum(1 for field in required_fields if field in result["extracted_data"])
        found_optional = sum(1 for field in optional_fields if field in result["extracted_data"])
        
        # Weight required fields more heavily
        confidence = (found_required * 15 + found_optional * 10) / (len(required_fields) * 15 + len(optional_fields) * 10) * 100
        result["confidence_score"] = round(confidence, 2)
        
        logger.info(f"Extraction completed with {result['confidence_score']}% confidence")
        
    except Exception as e:
        logger.error(f"Error during parsing: {e}")
        result["anomalies"].append(f"Parsing error: {str(e)}")
    
    return result

def validate_extracted_data(data, text):
    """Validate extracted data and generate consistency report."""
    consistency = {
        'all_required_fields_present': False,
        'dates_valid': True,
        'dates_logical': True,
        'organization_name_valid': False,
        'job_title_valid': False,
        'employee_name_valid': False,
        'manager_info_present': False
    }
    
    anomalies = []
    
    # Check required fields
    required_fields = ['org_name', 'job_title', 'employee_name', 'start_date', 'end_date']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        anomalies.append(f"Missing required fields: {', '.join(missing_fields)}")
    else:
        consistency['all_required_fields_present'] = True
    
    # Validate individual fields
    if data.get('org_name') and len(data['org_name']) > 2:
        consistency['organization_name_valid'] = True
    
    if data.get('job_title') and len(data['job_title']) > 2:
        consistency['job_title_valid'] = True
    
    if data.get('employee_name') and len(data['employee_name'].split()) >= 2:
        consistency['employee_name_valid'] = True
    
    # Validate dates
    if data.get('start_date') and data.get('end_date'):
        try:
            start_dt = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_dt = datetime.strptime(data['end_date'], '%Y-%m-%d')
            
            if end_dt <= start_dt:
                consistency['dates_logical'] = False
                anomalies.append("End date should be after start date")
            
            # Check if dates are reasonable
            current_date = datetime.now()
            if start_dt > current_date:
                anomalies.append("Start date is in the future")
            if (current_date - start_dt).days > 365 * 50:  # 50 years
                anomalies.append("Start date seems unreasonably old")
                
        except ValueError:
            consistency['dates_valid'] = False
            anomalies.append("Invalid date format in extracted dates")
    
    # Check manager info
    manager_fields = ['manager_name', 'manager_title', 'manager_contact']
    if any(field in data for field in manager_fields):
        consistency['manager_info_present'] = True
    
    return consistency, anomalies

def process_letter(file_path):
    """Process experience letter based on file extension."""
    ext = Path(file_path).suffix.lower()
    text = None
    
    # Support more file formats
    supported_formats = {'.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    if ext not in supported_formats:
        return {
            "error": f"Unsupported file format: {ext}. Supported formats: {', '.join(supported_formats)}", 
            "file_processed": file_path
        }

    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = extract_text_from_docx(file_path)
        elif ext == ".doc":
            text = extract_text_from_doc(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            text = extract_text_from_image(file_path)
        
        if not text:
            if not TESSERACT_AVAILABLE and ext == ".pdf":
                # Check if this PDF might need OCR by trying to detect if it has images
                return {
                    "error": f"Could not extract text from {file_path} - OCR not available for scanned documents",
                    "file_processed": file_path,
                    "requires_ocr": True
                }
            else:
                return {
                    "error": f"Could not extract text from {file_path}",
                    "file_processed": file_path
                }
        
        result = parse_letter(text)
        result["file_processed"] = file_path
        result["raw_text_length"] = len(text)
        
        logger.info(f"Successfully processed {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return {
            "error": f"Processing failed: {str(e)}",
            "file_processed": file_path
        }

def save_to_json(data, output_path):
    """Save parsed data to JSON file with proper formatting."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)
        logger.info(f"Output saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving JSON to {output_path}: {e}")

def main():
    """Process all experience letters in the uploads folder - individual outputs only."""
    uploads_dir = "uploads"
    outputs_dir = "outputs"
    
    # Create directories if they don't exist
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    if not os.path.exists(uploads_dir):
        print(f"Error: {uploads_dir} folder not found")
        return
    
    # Get all supported files
    supported_extensions = {'.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    files_to_process = []
    
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path) and Path(file_path).suffix.lower() in supported_extensions:
            files_to_process.append((file, file_path))
    
    if not files_to_process:
        print(f"No supported files found in {uploads_dir}. Supported formats: {', '.join(supported_extensions)}")
        return
    
    print(f"Found {len(files_to_process)} files to process...")
    
    # Show file types being processed
    file_types = {}
    for file, file_path in files_to_process:
        ext = Path(file_path).suffix.lower()
        file_types[ext] = file_types.get(ext, 0) + 1
    
    print(f"File types: {', '.join([f'{count} {ext}' for ext, count in file_types.items()])}")
    print()
    
    processed_count = 0
    error_count = 0
    ocr_needed_count = 0
    
    for file, file_path in files_to_process:
        print(f"Processing: {file}")
        
        try:
            result = process_letter(file_path)
            
            # Save individual result only
            output_path = os.path.join(outputs_dir, f"output_{file}.json")
            save_to_json(result, output_path)
            
            if 'error' not in result:
                processed_count += 1
                confidence = result.get('confidence_score', 0)
                print(f"  ✓ Success - Confidence: {confidence:.2f}%")
                
                # Show extracted job title for verification
                job_title = result.get('extracted_data', {}).get('job_title')
                org_name = result.get('extracted_data', {}).get('org_name')
                if job_title:
                    print(f"    Job Title: {job_title}")
                if org_name:
                    print(f"    Organization: {org_name}")
            else:
                error_count += 1
                error_msg = result['error']
                print(f"  ✗ Failed - {error_msg}")
                
                # Provide specific guidance based on error type
                if "OCR not available for scanned documents" in error_msg:
                    ocr_needed_count += 1
                    print(f"    📋 This appears to be a scanned document requiring OCR")
                    print(f"    💡 Install Tesseract OCR to process this file (see TESSERACT_SETUP.md)")
                elif "Could not extract text" in error_msg:
                    print(f"    📋 Text extraction failed - file may be corrupted or unsupported format")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ Failed - {str(e)}")
    
    # Print final summary without saving summary file
    print(f"\n{'='*50}")
    print("PROCESSING COMPLETE")
    print(f"{'='*50}")
    print(f"Total files processed: {len(files_to_process)}")
    print(f"Successful extractions: {processed_count}")
    print(f"Failed extractions: {error_count}")
    success_rate = (processed_count / len(files_to_process)) * 100 if files_to_process else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if ocr_needed_count > 0:
        print(f"\n🔍 OCR-dependent files: {ocr_needed_count}")
        print(f"💡 Install Tesseract OCR to process scanned documents")
        print(f"📖 See TESSERACT_SETUP.md for installation instructions")
    
    print(f"\nIndividual results saved to: {outputs_dir}")
    print("No summary file generated - each file has separate JSON output.")

if __name__ == "__main__":
    main()