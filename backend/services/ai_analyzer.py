import google.generativeai as genai
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import Dict, List, Tuple

class AIAnalyzer:
    def __init__(self):
        # Initialize Gemini
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def get_embeddings(self, text: str) -> np.ndarray:
        """Get embeddings for text"""
        try:
            embeddings = self.embedding_model.encode([text])
            return embeddings[0]
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity between resume and job description"""
        try:
            resume_embedding = self.get_embeddings(resume_text)
            job_embedding = self.get_embeddings(job_description)
            
            similarity = cosine_similarity([resume_embedding], [job_embedding])[0][0]
            return float(similarity)
        except Exception as e:
            raise Exception(f"Error calculating semantic similarity: {str(e)}")
    
    def extract_job_requirements(self, job_description: str) -> Dict:
        """Extract structured requirements from job description using Gemini"""
        try:
            prompt = f"""
            Analyze the following job description and extract structured information:
            
            Job Description:
            {job_description}
            
            Please extract and return in JSON format:
            1. required_skills: List of technical skills that are must-have
            2. preferred_skills: List of technical skills that are nice-to-have
            3. required_education: Minimum education requirements
            4. required_experience: Years of experience required
            5. key_responsibilities: Main job responsibilities
            6. company_info: Company name and industry
            
            Return only valid JSON format.
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            return result
        except Exception as e:
            # Fallback to basic extraction if Gemini fails
            return self._basic_job_analysis(job_description)
    
    def _basic_job_analysis(self, job_description: str) -> Dict:
        """Basic job analysis fallback"""
        # Simple keyword extraction
        skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
            'machine learning', 'data science', 'aws', 'docker', 'kubernetes',
            'git', 'github', 'agile', 'scrum', 'leadership', 'communication'
        ]
        
        found_skills = []
        job_lower = job_description.lower()
        
        for skill in skills_keywords:
            if skill in job_lower:
                found_skills.append(skill)
        
        return {
            'required_skills': found_skills[:5],  # Top 5 skills
            'preferred_skills': found_skills[5:],  # Remaining skills
            'required_education': 'Bachelor\'s degree',
            'required_experience': '2-5 years',
            'key_responsibilities': ['Develop software applications', 'Collaborate with team'],
            'company_info': {'name': 'Company', 'industry': 'Technology'}
        }
    
    def analyze_resume_fit(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Analyze how well resume fits job requirements using Gemini"""
        try:
            resume_text = resume_data.get('cleaned_text', '')
            resume_skills = resume_data.get('skills', [])
            
            prompt = f"""
            Analyze the following resume against the job requirements and provide a detailed assessment:
            
            Job Requirements:
            {json.dumps(job_requirements, indent=2)}
            
            Resume Content:
            {resume_text}
            
            Resume Skills Found:
            {', '.join(resume_skills)}
            
            Please provide analysis in JSON format with:
            1. relevance_score: Score from 0-100 indicating how well the resume matches the job
            2. verdict: "High", "Medium", or "Low" suitability
            3. missing_skills: List of required skills not found in resume
            4. missing_certifications: List of certifications that would help
            5. missing_projects: Types of projects that would strengthen the application
            6. improvement_suggestions: Specific actionable advice for the candidate
            7. strengths: What the candidate does well
            8. analysis_summary: Brief summary of the assessment
            
            Return only valid JSON format.
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            # Ensure score is within 0-100 range
            if 'relevance_score' in result:
                result['relevance_score'] = max(0, min(100, result['relevance_score']))
            
            return result
        except Exception as e:
            # Fallback analysis
            return self._fallback_analysis(resume_data, job_requirements)
    
    def _fallback_analysis(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Fallback analysis when Gemini fails"""
        resume_skills = resume_data.get('skills', [])
        required_skills = job_requirements.get('required_skills', [])
        preferred_skills = job_requirements.get('preferred_skills', [])
        
        # Calculate basic matching
        matched_required = len(set(resume_skills) & set([s.lower() for s in required_skills]))
        matched_preferred = len(set(resume_skills) & set([s.lower() for s in preferred_skills]))
        
        # Simple scoring
        required_score = (matched_required / max(len(required_skills), 1)) * 70
        preferred_score = (matched_preferred / max(len(preferred_skills), 1)) * 30
        total_score = min(100, required_score + preferred_score)
        
        # Determine verdict
        if total_score >= 70:
            verdict = "High"
        elif total_score >= 40:
            verdict = "Medium"
        else:
            verdict = "Low"
        
        # Find missing skills
        missing_skills = [skill for skill in required_skills if skill.lower() not in resume_skills]
        
        return {
            'relevance_score': total_score,
            'verdict': verdict,
            'missing_skills': missing_skills,
            'missing_certifications': ['AWS Certification', 'Google Cloud Certification'],
            'missing_projects': ['Web Application Project', 'Database Design Project'],
            'improvement_suggestions': [
                'Add more technical skills to your resume',
                'Include specific project examples',
                'Highlight relevant work experience'
            ],
            'strengths': ['Basic technical skills', 'Educational background'],
            'analysis_summary': f'Resume shows {verdict.lower()} suitability for this position'
        }
    
    def perform_comprehensive_analysis(self, resume_data: Dict, job_description: str) -> Dict:
        """Perform comprehensive resume analysis"""
        try:
            # Extract job requirements
            job_requirements = self.extract_job_requirements(job_description)
            
            # Calculate semantic similarity
            semantic_score = self.calculate_semantic_similarity(
                resume_data.get('cleaned_text', ''),
                job_description
            )
            
            # Analyze resume fit
            analysis_result = self.analyze_resume_fit(resume_data, job_requirements)
            
            # Combine results
            final_result = {
                'semantic_similarity': semantic_score,
                'job_requirements': job_requirements,
                **analysis_result
            }
            
            # Adjust final score based on semantic similarity
            if 'relevance_score' in final_result:
                semantic_adjustment = semantic_score * 20  # 0-20 points from semantic similarity
                final_result['relevance_score'] = min(100, 
                    (final_result['relevance_score'] * 0.8) + semantic_adjustment
                )
            
            return final_result
            
        except Exception as e:
            raise Exception(f"Error in comprehensive analysis: {str(e)}")
