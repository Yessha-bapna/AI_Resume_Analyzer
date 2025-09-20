# Resume Analyzer Setup Guide

This guide will help you set up and run the Resume Analyzer system on your local machine.

## Prerequisites

Before starting, make sure you have the following installed:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **PostgreSQL** (optional, SQLite will be used by default) - [Download here](https://www.postgresql.org/download/)
- **Git** - [Download here](https://git-scm.com/)

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo-url>
   cd Resume-Analyzer
   ```

2. **Run the setup script:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

3. **Follow the prompts** to configure your environment variables.

### Option 2: Manual Setup

#### 1. Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/resume_analyzer
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_here
   FLASK_ENV=development
   ```

5. **Initialize database:**
   ```bash
   python init_db.py
   ```

6. **Start the Flask server:**
   ```bash
   python app.py
   ```

#### 2. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/resume_analyzer
# Or use SQLite for development:
# DATABASE_URL=sqlite:///resume_analyzer.db

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Optional: Redis for Celery (if you plan to use background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Getting API Keys

#### Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add it to your `.env` file

#### Database Setup

**Option 1: SQLite (Default)**
- No additional setup required
- Database file will be created automatically

**Option 2: PostgreSQL**
1. Install PostgreSQL
2. Create a database:
   ```sql
   CREATE DATABASE resume_analyzer;
   ```
3. Update `DATABASE_URL` in your `.env` file

## Usage

### Starting the Application

1. **Start Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

### First Time Setup

1. **Create Admin Account:**
   - Go to http://localhost:3000/register
   - Register with admin privileges (contact your system administrator)
   - Or use the database initialization script

2. **Login as Admin:**
   - Go to http://localhost:3000/login
   - Use your admin credentials

3. **Create Job Posting:**
   - Navigate to Admin Dashboard
   - Click "Create Job Posting"
   - Fill in job details and requirements

4. **Upload Resumes:**
   - Users can register and upload their resumes
   - Resumes will be automatically analyzed against job postings

## Features

### For Administrators
- **Dashboard**: Overview of system statistics
- **Job Management**: Create, edit, and manage job postings
- **Resume Rankings**: View ranked resumes for each job posting
- **User Management**: Manage user accounts and permissions
- **System Analytics**: Monitor analysis performance and success rates

### For Users
- **Job Browsing**: View available job postings
- **Resume Upload**: Upload resumes in PDF or DOCX format
- **Analysis Results**: View detailed analysis results and scores
- **Improvement Suggestions**: Get personalized feedback for resume improvement

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   - Make sure you're in the correct virtual environment
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Database connection errors:**
   - Check your `DATABASE_URL` in `.env`
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - Try using SQLite for development

3. **API key errors:**
   - Verify your Gemini API key is correct
   - Check if you have API quota remaining

4. **Frontend not connecting to backend:**
   - Ensure Flask server is running on port 5001
   - Check for CORS errors in browser console

5. **File upload errors:**
   - Check file size (max 16MB)
   - Ensure file format is PDF or DOCX
   - Check if uploads directory exists and is writable

### Performance Optimization

1. **For Production:**
   - Use PostgreSQL instead of SQLite
   - Set up Redis for background task processing
   - Configure proper file storage (AWS S3, etc.)
   - Use a production WSGI server (Gunicorn)

2. **For Large Scale:**
   - Implement caching with Redis
   - Use CDN for static files
   - Set up horizontal scaling
   - Implement rate limiting

## Development

### Project Structure

```
Resume-Analyzer/
├── backend/                 # Flask backend
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── models.py           # Database models
│   ├── requirements.txt    # Python dependencies
│   └── app.py             # Flask application
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── contexts/      # React contexts
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── README.md              # Project overview
├── SETUP.md              # This setup guide
└── start.sh              # Automated setup script
```

### Adding New Features

1. **Backend API:**
   - Add routes in `backend/routes/`
   - Update models in `backend/models.py`
   - Add business logic in `backend/services/`

2. **Frontend:**
   - Add components in `frontend/src/components/`
   - Add pages in `frontend/src/pages/`
   - Update API services in `frontend/src/services/`

## Support

If you encounter any issues:

1. Check this setup guide
2. Review the troubleshooting section
3. Check the application logs
4. Create an issue in the project repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.
