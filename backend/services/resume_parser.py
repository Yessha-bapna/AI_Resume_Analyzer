import fitz  # PyMuPDF
import docx
import os
import re
from typing import Dict, List, Optional

class ResumeParser:
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
            'machine learning', 'data science', 'aws', 'docker', 'kubernetes',
            'git', 'github', 'agile', 'scrum', 'leadership', 'communication',
            'problem solving', 'teamwork', 'project management', 'analytics'
        ]
        
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'diploma', 'certification',
            'university', 'college', 'institute', 'school'
        ]
        
        self.experience_keywords = [
            'experience', 'work', 'job', 'position', 'role', 'internship',
            'freelance', 'consultant', 'manager', 'developer', 'engineer'
        ]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type.lower() == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type.lower() == 'docx':
            return self.extract_text_from_docx(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_type}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove common headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that might be headers/footers
            if len(line) > 3 and not line.isdigit():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        # Extract technical skills from patterns
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms like SQL, AWS, API
            r'\b\w+\s*\+{1,2}\b',  # Languages like C++, C#
            r'\b\w+\.(js|py|java|cpp|sql)\b'  # File extensions
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            found_skills.extend([match.lower() for match in matches])
        
        return list(set(found_skills))
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains education keywords
            if any(keyword in line_lower for keyword in self.education_keywords):
                education_info = {
                    'institution': line,
                    'details': ''
                }
                
                # Look for details in next few lines
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not any(keyword in next_line.lower() for keyword in self.experience_keywords):
                        education_info['details'] += next_line + ' '
                
                education.append(education_info)
        
        return education
    
    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains experience keywords
            if any(keyword in line_lower for keyword in self.experience_keywords):
                exp_info = {
                    'position': line,
                    'details': ''
                }
                
                # Look for details in next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and len(next_line) > 10:
                        exp_info['details'] += next_line + ' '
                
                experience.append(exp_info)
        
        return experience
    
    def extract_projects(self, text: str) -> List[str]:
        """Extract project information"""
        projects = []
        lines = text.split('\n')
        
        project_keywords = ['project', 'portfolio', 'github', 'repository']
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in project_keywords):
                if len(line.strip()) > 10:
                    projects.append(line.strip())
        
        return projects
    
    def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """Main parsing function"""
        try:
            # Extract raw text
            raw_text = self.extract_text(file_path, file_type)
            cleaned_text = self.clean_text(raw_text)
            
            # Extract structured information
            parsed_data = {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'skills': self.extract_skills(cleaned_text),
                'education': self.extract_education(cleaned_text),
                'experience': self.extract_experience(cleaned_text),
                'projects': self.extract_projects(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'char_count': len(cleaned_text)
            }
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"Error parsing resume: {str(e)}")
