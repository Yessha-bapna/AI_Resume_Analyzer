# Resume Analyzer System

An AI-powered resume evaluation system that compares resumes against job descriptions and provides relevance scores with ranking.

## Features

- **Admin Dashboard**: Upload job descriptions, view resume rankings
- **User Dashboard**: View job descriptions, upload resumes, see results
- **AI Analysis**: Uses Gemini LLM and embeddings for semantic matching
- **Dynamic Ranking**: Queue-based system with automatic reordering
- **Authentication**: Separate admin and user authentication

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
6. Run database migrations: `python manage.py db upgrade`
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
