import google.generativeai as genai
import os
import re
from typing import Dict, List, Any

class AIAnalyzer:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def perform_comprehensive_analysis(self, resume_data: Dict, job_description: str) -> Dict[str, Any]:
        """Perform comprehensive resume analysis using Gemini AI"""
        try:
            # Extract key information from resume
            resume_text = self._extract_resume_text(resume_data)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(resume_text, job_description)
            
            # Get AI analysis
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Parse the response
            return self._parse_analysis_response(analysis_text)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_resume_text(self, resume_data: Dict) -> str:
        """Extract and format resume text for analysis"""
        text_parts = []
        
        # Add personal information
        if resume_data.get('personal_info'):
            personal = resume_data['personal_info']
            text_parts.append(f"Name: {personal.get('name', 'N/A')}")
            text_parts.append(f"Email: {personal.get('email', 'N/A')}")
            text_parts.append(f"Phone: {personal.get('phone', 'N/A')}")
        
        # Add education
        if resume_data.get('education'):
            text_parts.append("\nEducation:")
            for edu in resume_data['education']:
                text_parts.append(f"- {edu.get('degree', '')} from {edu.get('institution', '')}")
        
        # Add experience
        if resume_data.get('experience'):
            text_parts.append("\nExperience:")
            for exp in resume_data['experience']:
                text_parts.append(f"- {exp.get('title', '')} at {exp.get('company', '')}")
                if exp.get('description'):
                    text_parts.append(f"  {exp['description']}")
        
        # Add skills
        if resume_data.get('skills'):
            text_parts.append(f"\nSkills: {', '.join(resume_data['skills'])}")
        
        # Add projects
        if resume_data.get('projects'):
            text_parts.append("\nProjects:")
            for proj in resume_data['projects']:
                text_parts.append(f"- {proj.get('name', '')}: {proj.get('description', '')}")
        
        return "\n".join(text_parts)
    
    def _create_analysis_prompt(self, resume_text: str, job_description: str) -> str:
        """Create a comprehensive analysis prompt for Gemini"""
        return f"""
        Analyze this resume against the job description and provide a detailed assessment.

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Please provide your analysis in the following JSON format:
        {{
            "relevance_score": 85,
            "verdict": "High",
            "missing_skills": ["Python", "Docker"],
            "missing_certifications": ["AWS Certified"],
            "missing_projects": ["Machine Learning Project"],
            "improvement_suggestions": [
                "Add more Python projects to your portfolio",
                "Consider getting AWS certification",
                "Include specific metrics in your experience descriptions"
            ],
            "strengths": [
                "Strong educational background",
                "Relevant work experience"
            ],
            "weaknesses": [
                "Limited project portfolio",
                "Missing some key technical skills"
            ]
        }}

        Scoring Guidelines:
        - 90-100: Exceptional match, highly recommended
        - 80-89: Strong match, good candidate
        - 70-79: Moderate match, acceptable with improvements
        - 60-69: Weak match, needs significant improvement
        - Below 60: Poor match, not recommended

        Verdict Guidelines:
        - High: 80+ score
        - Medium: 60-79 score
        - Low: Below 60 score

        Please ensure the response is valid JSON format only.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data"""
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
                
                # Validate and clean the response
                return {
                    'relevance_score': float(analysis.get('relevance_score', 0)),
                    'verdict': analysis.get('verdict', 'Low'),
                    'missing_skills': analysis.get('missing_skills', []),
                    'missing_certifications': analysis.get('missing_certifications', []),
                    'missing_projects': analysis.get('missing_projects', []),
                    'improvement_suggestions': analysis.get('improvement_suggestions', []),
                    'strengths': analysis.get('strengths', []),
                    'weaknesses': analysis.get('weaknesses', [])
                }
            else:
                return self._get_fallback_analysis()
                
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Provide fallback analysis when AI fails"""
        return {
            'relevance_score': 50.0,
            'verdict': 'Medium',
            'missing_skills': ['Technical skills need verification'],
            'missing_certifications': ['Relevant certifications recommended'],
            'missing_projects': ['Portfolio projects needed'],
            'improvement_suggestions': [
                'Please ensure all information is complete and accurate',
                'Consider adding more detailed project descriptions',
                'Verify technical skills and certifications'
            ],
            'strengths': ['Resume submitted successfully'],
            'weaknesses': ['Analysis incomplete due to technical issues']
        }
