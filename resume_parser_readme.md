# 🧠 Resume Parser & Candidate Fit Scorer

An advanced Python module that extracts structured resume data from PDF files and ranks candidates based on job fit. It uses regex, NLP, and heuristic rules to analyze resume content, anonymize personal details, and calculate job matching scores.

---

## ✨ Key Features

- 📄 **Resume Text Extraction** from PDFs
- 🧠 **Entity Extraction**:
  - Personal Info (Name, Email, Phone, LinkedIn, GitHub)
  - Education (Degree, Institution, Dates)
  - Experience (Company, Role, Dates, Achievements)
  - Skills (Technical & Soft)
  - Certifications, Languages
- 🔐 **Anonymization** of PII for bias-free review
- 📊 **Fit Score Calculator** based on job description
- 📌 **Ranking & Shortlisting** based on fit score
- 📁 **Batch Processing** of multiple resumes
- ✅ Outputs structured JSON data

---

## 🧰 Main Workflow: `main()`

### Purpose:

Tests the `EnhancedPDFExtractor` class by:

- Loading a sample job description
- Processing one test resume PDF
- Running batch processing on all resumes in `UPLOADS_DIR`
- Saving results with anonymized data and fit scores

### Calls:

- `EnhancedPDFExtractor.process_pdf()` – handles single file processing
- `EnhancedPDFExtractor.batch_process()` – handles batch processing

---

## 🧠 Class: `EnhancedPDFExtractor`

Main class that coordinates extraction, parsing, scoring, anonymization, and saving.

### Key Methods & Their Responsibilities:

---

### 🔍 `extract_text_from_pdf(pdf_path)`

- Uses `pdfplumber` to read text from PDF
- Returns text and page count

---

### 📊 `classify_document(filename, text)`

- Identifies if the document is a resume or other type
- Returns type and confidence score

---

### 🧱 `extract_entities(text, filename)`

- Central method to extract all resume components:
  - Calls sub-methods:
    - `_extract_personal_info()`
    - `_extract_education()`
    - `_extract_experience()`
    - `_extract_skills()`
    - `_extract_certifications()`
    - `_extract_languages()`
  - Returns full structured resume entity dictionary

---

### 👤 `_extract_personal_info()`

- Extracts name, phone, email, LinkedIn, GitHub, location

---

### 🎓 `_extract_education()`

- Detects and parses Education section
- Extracts degree, institution, and dates

---

### 💼 `_extract_experience()`

- Extracts Company, Designation, Dates, Achievements
- Uses bullet points or line breaks to separate jobs

---

### 🧑‍💻 `_extract_skills()`

- Categorizes skills as Technical or Soft
- Matches from predefined lists in both the resume and job description

---

### 🏅 `_extract_certifications()`

- Looks for known certification headings and extracts valid lines

---

### 🗣️ `_extract_languages()`

- Identifies languages known or mentioned

---

### 🔒 `anonymize_entities(entities)`

- Redacts PII (Name, Email, Phone, LinkedIn, GitHub, Location)
- Replaces institutions and company names with placeholders

---

### 🧮 `calculate_fit_score(entities, job_description)`

- Assigns weights and scores to resume based on JD match
- Criteria:
  - Skills Match (40%)
  - Experience Relevance (30%)
  - Education Match (20%)
  - Tenure Stability (5%)
  - Growth Trajectory (5%)
- Returns dictionary of scores

---

### 📊 `rank_candidates(candidates, job_description)`

- Ranks all candidates by `total_fit` score
- Adds `rank` field to each

---

### ✅ `shortlist_candidates(ranked_candidates, threshold=70, max_candidates=None)`

- Selects top candidates above threshold
- Flags each as `shortlisted: True` or `False`

---

### 📁 `process_pdf(pdf_path, job_description=None, anonymize=False)`

#### Purpose:

Main function for processing a single resume

#### Steps:

1. Extracts text from PDF
2. Classifies document
3. Parses resume entities
4. Anonymizes (optional)
5. Scores against JD (if provided)
6. Returns structured dictionary

#### Calls:

- `extract_text_from_pdf()`
- `classify_document()`
- `extract_entities()`
- `anonymize_entities()`
- `calculate_fit_score()`

---

### 📦 `batch_process(pdf_dir, job_description=None, anonymize=False)`

#### Purpose:

Process all PDFs in directory

#### Steps:

1. Finds all `.pdf` files
2. Calls `process_pdf()` on each
3. Saves:
   - Raw results
   - Ranked results (if JD is given)

---

## 📁 Project Structure

```
your_project/
│
├── uploads_resumes/           # Input resumes in PDF format
├── processed_results/         # JSON outputs
├── extractor_module.py        # Contains EnhancedPDFExtractor class
└── README.md                  # This documentation
```

---

## ✅ Setup Instructions

1. **Install dependencies**:

```bash
pip install pdfplumber spacy
python -m spacy download en_core_web_sm
```

2. **Prepare directories**:

- Place resumes in `uploads_resumes/`

3. **Run main script**:

```bash
python extractor_module.py
```

---

## 📊 Sample Output (JSON)

```json
{
  "entities": {
    "personal_info": {
      "name": "[NAME REDACTED]",
      "email": "[EMAIL REDACTED]",
      "phone": "[PHONE REDACTED]"
    },
    "education": [
      {"degree": "B.Tech in Computer Science", "institution": "[INSTITUTION REDACTED]"}
    ],
    "experience": [
      {"company": "[COMPANY REDACTED]", "position": "Software Engineer"}
    ],
    "skills": {
      "technical": ["Python", "React"],
      "soft": ["Teamwork", "Communication"]
    }
  },
  "fit_scores": {
    "skills_match": 80,
    "experience_relevance": 60,
    "education_match": 90,
    "tenure_stability": 80,
    "growth_trajectory": 90,
    "total_fit": 78.5
  },
  "shortlisted": true
}
```

---

## 🤝 Credits

- `pdfplumber`, `spaCy`, `json`, `re`, `datetime`
- Developed for NeoAI HRMS to automate candidate screening

---

## 📄 License

MIT License – free for commercial and non-commercial use.

