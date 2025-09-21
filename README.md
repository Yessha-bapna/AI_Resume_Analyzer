
# AI Resume Analyzer System

<p align="center">
  <img src="./frontend/assets/Screenshot (358).png" width="700"/>
</p> 

> **Note:** Replace the above image with your actual website screenshot.

## Problem Statement

At Innomatics Research Labs, resume evaluation is currently manual, inconsistent, and time-consuming. Every week, the placement team across Hyderabad, Bangalore, Pune, and Delhi NCR receives 18–20 job requirements, with each posting attracting thousands of applications.

Currently, recruiters and mentors manually review resumes, matching them against job descriptions (JD). This leads to:
- Delays in shortlisting candidates.
- Inconsistent judgments, as evaluators may interpret role requirements differently.
- High workload for placement staff, reducing their ability to focus on interview prep and student guidance.

With hiring companies expecting fast and high-quality shortlists, there is a pressing need for an automated system that can scale, be consistent, and provide actionable feedback to students.

## Objective

The Automated Resume Relevance Check System will:
- Automate resume evaluation against job requirements at scale.
- Generate a Relevance Score (0–100) for each resume per job role.
- Highlight gaps such as missing skills, certifications, or projects.
- Provide a fit verdict (High / Medium / Low suitability) to recruiters.
- Offer personalized improvement feedback to students.
- Store evaluations in a web-based dashboard accessible to the placement team.

This system is designed to be robust, scalable, and flexible enough to handle thousands of resumes weekly.

## Sample Data

Sample job descriptions and resumes are provided in the `Theme 2 - Sample Data/` folder.

## Proposed Solution

We propose building an AI-powered resume evaluation engine that combines rule-based checks with LLM-based semantic understanding.

**Key Features:**
- Accept resumes (PDF/DOCX) uploaded by students.
- Accept job descriptions uploaded by the placement team.
- Use text extraction + embeddings to compare resume content with job descriptions.
- Run hybrid scoring:
  - Hard match (keywords, skills, education)
  - Soft match (semantic fit via embeddings + LLM reasoning)
- Output a Relevance Score, Missing Elements, and Verdict.
- Store results for the placement team in a searchable web application dashboard.

This approach ensures both speed (hard checks) and contextual understanding (LLM-powered checks).

## Workflow

1. **Job Requirement Upload** - Placement team uploads job description (JD).
2. **Resume Upload** - Students upload resumes while applying.
3. **Resume Parsing**
	- Extract raw text from PDF/DOCX.
	- Standardize formats (remove headers/footers, normalize sections).
4. **JD Parsing**
	- Extract role title, must-have skills, good-to-have skills, qualifications.
5. **Relevance Analysis**
	- **Step 1: Hard Match** – keyword & skill check (exact and fuzzy matches).
	- **Step 2: Semantic Match** – embedding similarity between resume and JD using LLMs.
	- **Step 3: Scoring & Verdict** – Weighted scoring formula for final score.
6. **Output Generation**
	- Relevance Score (0–100).
	- Missing Skills/Projects/Certifications.
	- Verdict (High / Medium / Low suitability).
	- Suggestions for student improvement.
7. **Storage & Access**
	- Results stored in the database.
	- The placement team can search/filter resumes by job role, score, and location.

## Web Application

### Admin Dashboard

<img src="./frontend/assets/Screenshot (361).png" alt="Admin Dashboard" width="700"/>

<img src="./frontend/assets/Screenshot (362).png" alt="Admin Dashboard" width="700"/>

<img src="./frontend/assets/Screenshot (364).png" alt="Admin Dashboard" width="700"/>


- Upload job descriptions
- View and filter ranked resumes for each job
- Download reports

### User Dashboard

<img src="./frontend/assets/Screenshot (360).png" width="700"/>

- Register/login
- View available job descriptions
- Upload resumes for specific jobs
- View analysis results, missing skills, and suggestions

### AI Analysis

<img src="frontend/src/assets/Screenshot (360).png" width="700"/>

- Uses Gemini LLM and sentence embeddings for semantic matching
- Combines hard and soft matching for robust scoring

### Dynamic Ranking
- Queue-based system with automatic reordering as new resumes are analyzed

### Authentication

<img src="./frontend/assets/Screenshot (358).png" alt="Admin Dashboard" width="700"/>

- Separate admin and user authentication for secure access

## Tech Stack

### Backend
- Flask (Python web framework)
- PostgreSQL (Database)
- Gemini LLM (AI analysis)
- Sentence Transformers (Embeddings)
- PyMuPDF/pdfplumber (PDF parsing)
- python-docx (DOCX parsing)

### Frontend
- React with Vite
- Tailwind CSS
- Axios (API calls)
- React Router

## Setup Instructions

### Backend Setup
1. Navigate to backend directory
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables in `.env`
6. Run database migrations: `python manage.py db upgrade` (if applicable)
7. Start server: `python app.py`

### Frontend Setup
1. Navigate to frontend directory
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`

## Environment Variables

Create a `.env` file in the backend directory:
```
DATABASE_URL=postgresql://username:password@localhost/resume_analyzer
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

## Usage

1. **Admin**: Login and upload job descriptions
2. **Users**: Register/login, view jobs, upload resumes
3. **System**: Automatically analyzes resumes and updates rankings
4. **Results**: View scores, missing skills, and improvement suggestions

## Contribution

Contributions are welcome! Please open issues or submit pull requests for improvements.

## License

This project is for educational and hackathon purposes.
