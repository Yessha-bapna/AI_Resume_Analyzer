# Debugging Guide for Resume Analyzer

## Current Issue: New User Applications Not Showing in Rankings

### Problem Analysis:
- ✅ Rankings system is working (1 analysis showing)
- ✅ Database is working (PostgreSQL with persistent data)
- ✅ Backend is running properly
- ❌ New user applications not appearing in rankings

### Root Cause:
The new user (yessha) needs to complete the full application flow:

1. **Upload Resume** → Resume stored in database
2. **Apply for Job** → Application created + Analysis triggered
3. **Analysis Completes** → Results stored + Ranking updated
4. **Admin Sees Rankings** → New analysis appears in rankings

### Step-by-Step Testing:

#### Step 1: Login as New User
```bash
# Login as the new user (yessha)
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "yessha", "password": "user_password"}' \
  -c user_cookies.txt
```

#### Step 2: Upload Resume
```bash
# Upload a resume file
curl -X POST http://localhost:5001/api/resumes/upload \
  -b user_cookies.txt \
  -F "file=@/path/to/resume.pdf"
```

#### Step 3: Apply for Job
```bash
# Apply for job (replace resume_id with actual ID from step 2)
curl -X POST http://localhost:5001/api/applications \
  -H "Content-Type: application/json" \
  -b user_cookies.txt \
  -d '{"job_id": 1, "resume_id": 2}'
```

#### Step 4: Check Analysis Progress
Watch backend console for:
```
Starting analysis for resume 2 and job 1
Resume parsed successfully
Starting AI analysis...
AI analysis completed with score: XX
Adding to ranking system...
Successfully added to ranking system
Analysis completed successfully for resume 2
```

#### Step 5: Verify Rankings
```bash
# Login as admin and check rankings
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c admin_cookies.txt

curl -X GET http://localhost:5001/api/admin/jobs/1/rankings \
  -b admin_cookies.txt
```

### Common Issues:

1. **No Resume Uploaded**: User must upload resume before applying
2. **Analysis Failing**: Check backend logs for AI analysis errors
3. **Ranking System Error**: Check for database session issues
4. **Authentication Issues**: Ensure user is logged in properly

### Debugging Commands:

```bash
# Check if user has resumes
curl -X GET http://localhost:5001/api/resumes/ -b user_cookies.txt

# Check if user has applications
curl -X GET http://localhost:5001/api/applications/ -b user_cookies.txt

# Check if user has analyses
curl -X GET http://localhost:5001/api/resumes/analyses -b user_cookies.txt

# Check all analyses (admin only)
curl -X GET http://localhost:5001/api/admin/analyses -b admin_cookies.txt
```

### Expected Results:
After completing the flow, you should see:
- **2 rankings** in the admin page (instead of 1)
- **New analysis** with relevance score and verdict
- **Updated queue status** showing completed analyses

### Next Steps:
1. Have the new user (yessha) upload a resume
2. Apply for a job using that resume
3. Check backend logs for analysis progress
4. Verify rankings are updated
