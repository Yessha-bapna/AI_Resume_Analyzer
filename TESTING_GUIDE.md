# Resume Analyzer Testing Guide

## How to Test the Application Flow

### Step 1: Upload a Resume
1. Go to **Upload Resume** page
2. Select a PDF or DOCX resume file
3. Click **Upload Resume**
4. Wait for upload to complete

### Step 2: Apply for a Job
1. Go to **Jobs** page
2. Find a job you want to apply for
3. Click **Apply Now** button
4. Select your uploaded resume from the modal
5. Click **Apply Now**

### Step 3: Check Analysis Status
The resume analysis happens automatically in the background after applying. You can check:

1. **My Applications** page - See your application status
2. **My Resumes** page - See analysis results for your resumes
3. **Admin Dashboard** - See ranked applications (if you're admin)

### Step 4: Debug Analysis (If Needed)
If analysis isn't working, you can manually trigger it:

```bash
# Login first
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c cookies.txt

# Test analysis (replace resume_id and job_id)
curl -X POST http://localhost:5001/api/applications/test-analysis/1/1 \
  -b cookies.txt
```

### Expected Flow:
1. **Apply for job** → Application created
2. **Background analysis starts** → Resume parsed and analyzed
3. **Analysis completed** → Results stored and ranked
4. **Ranking updated** → High-scoring resumes promoted

### Troubleshooting:
- **No resumes uploaded**: Upload a resume first
- **Analysis not starting**: Check backend logs for errors
- **Analysis failing**: Check if GEMINI_API_KEY is set
- **No ranking**: Check if analysis completed successfully

### Backend Logs:
Watch the backend console for analysis progress:
```
Starting analysis for resume 1 and job 1
Resume parsed successfully
Starting AI analysis...
AI analysis completed with score: 85
Adding to ranking system...
Analysis completed successfully for resume 1
```
