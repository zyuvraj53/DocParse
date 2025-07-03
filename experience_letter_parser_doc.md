# Experience Letter Parser - Documentation

## Overview

This Python-based module automates the extraction of structured data from **experience letters** in various formats (PDF, DOCX, scanned images). It uses a combination of:

- OCR (Tesseract via pytesseract) for image-based documents
- NLP & regex for robust pattern matching
- Fallbacks for non-standard or noisy document formats

It returns a **structured JSON output** with:

- Employee name
- Job title
- Organization name
- Start and end dates
- Duration in years
- Manager name and contact (if available)
- Confidence score and anomaly detection

## Key Features

- ✅ Supports multiple file formats: `.pdf`, `.docx`, `.doc`, `.jpg`, `.png`, etc.
- 🔍 Multi-pattern entity extraction: name, title, dates, org, manager
- 🧠 Intelligent fallback handling with OCR for scanned files
- 📈 Confidence scoring and validation consistency checks
- 📁 Individual JSON output per file (no summary aggregation)

---

## Directory Structure

```bash
.
├── uploads/             # Drop your experience letters here
├── outputs/             # Processed JSON files are saved here
├── experience_parser.py # Main script
├── TESSERACT_SETUP.md   # Guide to install/configure Tesseract OCR
```

---

## How It Works

1. **File detection**: Script checks `uploads/` for supported files
2. **Text extraction**: Based on extension, uses pdfplumber/docx/ocr
3. **Cleaning**: Text normalized to reduce noise and OCR artifacts
4. **Entity Extraction**:
   - Dates: Uses regex + `dateparser` (if available)
   - Organization: Based on known phrases and document structure
   - Job Title: Fuzzy matching with known roles
   - Employee Name: Multiple robust name patterns
   - Manager Info: Optional fields (name, contact)
5. **Validation & Scoring**:
   - Missing fields/anomalies flagged
   - Logical date checks (e.g., start < end)
   - Confidence % based on fields found
6. **Output**:
   - JSON file for each processed letter in `outputs/`

---

## Requirements

Install required packages:

```bash
pip install pdfplumber python-docx pytesseract pillow
pip install dateparser fuzzywuzzy python-Levenshtein  # optional but improves results
```

Ensure [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) is installed and configured.

---

## Running the Parser

1. Place your files in the `uploads/` directory
2. Run the script:

```bash
python experience_parser.py
```

3. Check `outputs/` folder for per-file JSONs

---

## Sample Output

```json
{
  "file_processed": "uploads/letter1.pdf",
  "extracted_data": {
    "employee_name": "Ravi Sharma",
    "job_title": "Software Engineer",
    "org_name": "TechnoSpark Pvt Ltd",
    "start_date": "2019-06-01",
    "end_date": "2022-08-31",
    "duration_years": 3.25,
    "manager_name": "Anita Verma",
    "manager_contact": "anita@technospark.com"
  },
  "confidence_score": 93.33,
  "formatting_consistency": {
    "all_required_fields_present": true,
    "dates_valid": true,
    "dates_logical": true,
    "organization_name_valid": true,
    "job_title_valid": true,
    "employee_name_valid": true,
    "manager_info_present": true
  },
  "anomalies": []
}
```

---

## 🔍 Detailed Function Descriptions

### `main()`

- Entry point of the script.
- Iterates through files in `uploads/`
- For each file, calls `process_letter(file_path)`
- Saves output JSON to `outputs/`

### `process_letter(file_path)`

- Determines file type
- Calls:
  - `extract_text_from_pdf` for PDFs
  - `extract_text_from_docx` for DOCX
  - `extract_text_from_doc` or OCR fallback for DOC
  - `extract_text_from_image` for image files
- Calls `parse_letter(text)`
- Returns extracted data dict with score and anomalies

### `parse_letter(text)`

- Cleans text using `clean_text`
- Extracts:
  - `extract_dates_from_text`
  - `extract_organization_name`
  - `extract_employee_name`
  - `extract_job_title`
  - `extract_manager_info`
- Validates data via `validate_extracted_data`
- Computes confidence score based on field coverage

### `extract_text_from_pdf(file_path)`

- Uses `pdfplumber` to read text page-wise
- If empty, falls back to OCR with `pytesseract`

### `extract_text_from_docx(file_path)`

- Uses `python-docx` to read paragraphs and join them

### `extract_text_from_doc(file_path)`

- Tries parsing with docx method, falls back to OCR

### `extract_text_from_image(file_path)`

- Uses `pytesseract` to extract text from image

### `clean_text(text)`

- Normalizes whitespace
- Replaces common OCR artifacts (e.g., “l” instead of “1”)

### `extract_dates_from_text(text)`

- Uses regex patterns to extract potential dates
- Applies context to assign start/end
- Optionally uses `dateparser` to normalize

### `extract_organization_name(text)`

- Uses keyword patterns (e.g., “certify that”, “at”, “working in”)
- Cleans and returns organization name

### `extract_employee_name(text)`

- Searches for name patterns near phrases like "employee", "certify", or salutation
- Handles initials and mixed name orders

### `extract_job_title(text)`

- Uses regex + fuzzy match against job title list (if available)

### `extract_manager_info(text)`

- Searches for patterns like “reporting to”, “under supervision of”, etc.
- Extracts name and email/phone if found

### `validate_extracted_data(data, text)`

- Checks for:
  - Missing required fields
  - Start date < End date
  - Duplicate/conflicting values
- Returns validation report + anomalies

### `save_to_json(data, output_path)`

- Writes JSON file with UTF-8 encoding

---

## Troubleshooting

- **"OCR not available" error**: Install Tesseract and update `pytesseract.pytesseract.tesseract_cmd`
- **Garbage characters or missing text**: May require manual OCR tuning or clearer scans

---

## Tesseract Setup (Windows)

1. Download from: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and note the path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)
3. Update this line if needed:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
   ```

---
