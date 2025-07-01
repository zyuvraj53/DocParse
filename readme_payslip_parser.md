# 🧾 Payslip Parser

An automated Python script that extracts salary and employee details from payslips in various formats — PDF, DOCX, and image files (JPG, PNG).

---

## ✨ Key Features

- ✅ Multi-format support: PDF, DOCX, JPG, PNG
- 🔍 Extracts key salary components:
  - Basic Salary
  - HRA
  - Variable Pay / Incentives
  - Total Earnings & Deductions
  - Net Pay / Net Salary
- 👤 Extracts employee details:
  - Name
  - Employee ID
  - Designation
- 🧠 Smart parsing using regex patterns
- 🖼️ Uses Tesseract OCR for image-based payslips
- 📝 Outputs structured JSON results

---

## 🧠 `main()` – Orchestrator Function

### Purpose:

Controls the overall workflow from reading all payslip files in the `uploads_payslips/` folder to extracting information and saving JSON outputs in `outputs_payslips/`.

### Responsibilities:

- Ensure required directories exist
- Loop through all supported files
- Call:
  - `process_payslip()` to detect format and extract text
  - `parse_payslip()` to extract structured fields
  - `save_to_json()` to store results
- Print save confirmations

---

## 📂 File Processing Logic

### 🔍 `process_payslip(file_path)`

- Detects file type
- Chooses correct extractor:
  - `.pdf` → `extract_text_from_pdf()`
  - `.docx` → `extract_text_from_docx()`
  - `.jpg`, `.png` → `extract_text_from_image()`
- Parses using `parse_payslip()`
- Returns result with `file_processed`

---

## 🧾 Text Extraction Functions

### 📄 `extract_text_from_pdf(file_path)`

- Uses `pdfplumber` to extract text from PDF files
- Returns: Raw text or `None`

### 📄 `extract_text_from_docx(file_path)`

- Uses `python-docx` to extract text from DOCX files
- Extracts both paragraphs and tables
- Returns: Cleaned string

### 🖼️ `extract_text_from_image(file_path)`

- Uses `pytesseract` + `PIL.Image` for OCR
- Supported: `.jpg`, `.jpeg`, `.png`
- Returns: OCR result text

---

## 🧠 Core Extraction Logic

### 🧠 `parse_payslip(text)`

#### Purpose:

Extract salary components and employee info using multiple regex patterns.

#### Responsibilities:

- Clean text (remove currency symbols, tabs, etc.)
- Define regex patterns for multiple field variants
- Extract fields:
  - `basic`, `hra`, `variable_pay`, `net_pay`, etc.
  - `employee_name`, `employee_id`, `designation`
- Heuristics:
  - If `net_pay` is missing, try to guess from bottom lines
  - Compute total earnings if not present
- Output structure:

```json
{
  "components": {"basic": ..., "net_pay": ...},
  "employment_proof": {"employee_name": ..., "valid": true/false}
}
```

---

## 🗃️ Output & Saving

### 💾 `save_to_json(data, output_path)`

- Writes structured result to `outputs_payslips/output_<filename>.json`
- Uses: `json.dump()` with indent
- Handles errors gracefully

---

## 📁 Directory Structure

```
your_project/
│
├── uploads_payslips/         # Input: PDF/DOCX/Image payslips
├── outputs_payslips/         # Output: JSON results
├── payslip_parser.py         # Main script
└── README.md                 # This documentation
```

---

## ✅ Setup Instructions

1. **Install Python dependencies**:

```bash
pip install pdfplumber python-docx pytesseract pillow
```

2. **Install Tesseract**:

- [Windows download](https://github.com/tesseract-ocr/tesseract)
- Ubuntu/Debian:

```bash
sudo apt install tesseract-ocr
```

---

## 🚀 How to Use

1. Place files into `uploads_payslips/`
2. Run the script:

```bash
python payslip_parser.py
```

3. Check extracted data in `outputs_payslips/`

---

## 📬 Sample Output (JSON)

```json
{
  "components": {
    "basic": 15000.0,
    "hra": 5000.0,
    "variable_pay": 3000.0,
    "net_pay": 20000.0,
    "net_salary": 20000.0
  },
  "employment_proof": {
    "employee_name": "John Doe",
    "employee_id": "EMP12345",
    "designation": "Software Engineer",
    "valid": true
  },
  "file_processed": "uploads_payslips/payslip1.pdf"
}
```

---

## 🤝 Credits

- `pdfplumber`, `python-docx`, `pytesseract`, `Pillow`
- Designed for general Indian salary slip formats

---

## 📄 License

MIT License – use freely with credit.

