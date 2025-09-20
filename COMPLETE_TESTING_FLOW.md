# Complete Testing Flow for Resume Analyzer

## Why Rankings Are Empty

The rankings page shows empty because **no applications have been made yet**. The system works as follows:

1. **User uploads resume** → Resume stored in database
2. **User applies for job** → Application created + Analysis triggered
3. **Analysis completes** → Results stored + Ranking updated
4. **Admin sees rankings** → Ranked applications displayed

## Step-by-Step Testing

### 1. Create a Test User (if needed)
```bash
# Register a new user
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "test123"}'
```

### 2. Upload a Resume
1. Go to **http://localhost:3000/upload-resume**
2. Select a PDF or DOCX resume file
3. Click **Upload Resume**
4. Wait for upload to complete

### 3. Apply for a Job
1. Go to **http://localhost:3000/jobs**
2. Find the job you want to apply for
3. Click **Apply Now** button
4. Select your uploaded resume from the modal
5. Click **Apply Now**

### 4. Check Analysis Progress
Watch the backend console for analysis progress:
```
Starting analysis for resume 1 and job 1
Resume parsed successfully
Starting AI analysis...
AI analysis completed with score: 85
Adding to ranking system...
Analysis completed successfully for resume 1
```

### 5. View Rankings
1. Go to **http://localhost:3000/admin/jobs/1/rankings**
2. You should now see the ranked applications

## Manual Testing (API)

### Upload Resume
```bash
# Login as user
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}' \
  -c cookies.txt

# Upload resume
curl -X POST http://localhost:5001/api/resumes/upload \
  -b cookies.txt \
  -F "file=@/path/to/your/resume.pdf"
```

### Apply for Job
```bash
# Apply for job (replace resume_id and job_id)
curl -X POST http://localhost:5001/api/applications \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"job_id": 1, "resume_id": 1}'
```

### Check Rankings (as admin)
```bash
# Login as admin
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c admin_cookies.txt

# Check rankings
curl -X GET http://localhost:5001/api/admin/jobs/1/rankings \
  -b admin_cookies.txt
```

## Expected Results

After completing the flow, you should see:

1. **Applications**: In "My Applications" page
2. **Analyses**: In "My Resumes" page with scores
3. **Rankings**: In admin rankings page with ranked applications
4. **Backend Logs**: Detailed analysis progress

## Troubleshooting

- **No resumes**: Upload a resume first
- **No applications**: Apply for a job after uploading resume
- **No analyses**: Check backend logs for analysis errors
- **No rankings**: Ensure analyses completed successfully

## Current Status

✅ **Backend Running**: All APIs working
✅ **Frontend Running**: All pages accessible
✅ **Database Ready**: All tables created
✅ **Authentication Working**: Login/logout functional
❌ **No Data**: No resumes, applications, or analyses yet

**Next Step**: Follow the testing flow above to create data and see rankings!
