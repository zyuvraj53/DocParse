# DocParse
- Tool for parsing documents
- React.js + FastAPI + CockroachDB

# Folder Structure

```
.
├── client
│  ├── eslint.config.js
│  ├── index.html
│  ├── package-lock.json
│  ├── package.json
│  ├── public
│  │  └── vite.svg
│  ├── README.md
│  ├── src
│  │  ├── App.css
│  │  ├── App.jsx
│  │  ├── assets
│  │  │  └── react.svg
│  │  ├── components
│  │  │  ├── DarkModeToggle
│  │  │  │  └── index.jsx
│  │  │  ├── Hamburger
│  │  │  │  └── index.jsx
│  │  │  ├── Navbar
│  │  │  │  ├── index.css
│  │  │  │  └── index.jsx
│  │  │  └── Sidebar
│  │  │     ├── index.css
│  │  │     └── index.jsx
│  │  ├── index.css
│  │  ├── main.jsx
│  │  └── pages
│  │     ├── ExpenseReimbParser
│  │     ├── JoiningDocParser
│  │     │  ├── EdCertParser
│  │     │  │  ├── index.css
│  │     │  │  └── index.jsx
│  │     │  ├── ExperienceLetterParser
│  │     │  │  ├── index.css
│  │     │  │  └── index.jsx
│  │     │  ├── index.css
│  │     │  ├── index.jsx
│  │     │  └── PayslipParser
│  │     │     ├── index.css
│  │     │     └── index.jsx
│  │     └── ResumeParser
│  │        ├── index.css
│  │        ├── index.jsx
│  │        └── info.txt
│  ├── tailwind.config.js
│  └── vite.config.js
├── server
│  ├── config
│  │  └── database.py
│  ├── example_pdfs
│  ├── experience_letter_parser
│  │  └── parser.py
│  ├── main.py
│  ├── models
│  │  └── models.py
│  ├── payslip_parser
│  │  └── parser.py
│  ├── pdf_extractor
│  │  └── extractor.py
│  ├── processed
│  ├── processed_resumes
│  ├── requirements.txt
│  ├── routes
│  │  ├── __init__.py
│  │  └── route.py
│  ├── schema
│  │  └── schemas.py
│  ├── uploads
│  ├── uploads_experience_letters
│  ├── uploads_payslips
│  ├── uploads_resume
│  └── uploads_resumes
│
├── LICENSE
└── README.md
```

## Clint

## Server

 ### `config/database.py`

 - Establishes a SQLAlchemy connection to a CockroachDB instance using the provided `DATABASE_URL`.
  - Patches SQLAlchemy’s PostgreSQL dialect to correctly parse CockroachDB version strings.
  - Initializes the database engine and session factory (`SessionLocal`) for ORM operations.
  - Defines a `get_db()` generator function to provide and clean up database sessions (used in FastAPI dependencies).

 ### `experience_letter_parser/parser.py`
 -
 
 ### `models/model.py`
 -

 ### `payslip_parser/parer.py`
 -

 ### `pdf_extractor/extractor.py`
 -

 ### `processed/`
 -

 ### `processed_resumes/`
 -

 ### `routes/`

 - #### `routes/__init__.py`
 -

 - #### `routes/route.py`
 -

 ### `schema/schemas.py`
 -

│  ├── uploads_experience_letters
│  ├── uploads_payslips
│  ├── uploads_resume
│  └── uploads_resumes

## Database

##### Downlaod the app called beekeeper, and go to structure, then relations

- About the database

### ER_Diagrams

- The Resumes schema

 ![resumes](server/schema/resumes.png)
- The Experience Letter schema

 ![experience_letter](server/schema/experience.png)

- The payslips schema
 ![payslips](server/schema/payslips.png)


### Table

- The various tables, in the order of their relations, nested within them

### Relations

- The relations between the tables, and their types.

### Keys

- Foreign keys
- Primary keys
- Compound keys
