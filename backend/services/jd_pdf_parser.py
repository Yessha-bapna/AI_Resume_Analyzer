"""
Job Description PDF Parser Service
Extracts text from uploaded job description PDF files for resume analysis
"""
import PyPDF2
import fitz  # PyMuPDF
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class JDPDFParser:
    """Parser for extracting text from job description PDF files"""
    
    @staticmethod
    def extract_text(pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Optional[str]: Extracted text or None if extraction fails
        """
        try:
            # Try PyMuPDF first (faster and more reliable)
            text = JDPDFParser._extract_with_pymupdf(pdf_path)
            if text:
                return text
            
            # Fallback to PyPDF2
            text = JDPDFParser._extract_with_pypdf2(pdf_path)
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_with_pymupdf(pdf_path: str) -> Optional[str]:
        """Extract text using PyMuPDF (fitz)"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            
            # Clean up the text
            text = text.strip()
            if text:
                return text
            return None
            
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed for {pdf_path}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_with_pypdf2(pdf_path: str) -> Optional[str]:
        """Extract text using PyPDF2 (fallback)"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                
                # Clean up the text
                text = text.strip()
                if text:
                    return text
                return None
                
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed for {pdf_path}: {str(e)}")
            return None
    
    @staticmethod
    def get_combined_job_description(job) -> str:
        """
        Get combined job description from text fields and PDF
        
        Args:
            job: JobDescription model instance
            
        Returns:
            str: Combined job description text
        """
        combined_text = ""
        
        # Add text description
        if job.description:
            combined_text += f"Job Description:\n{job.description}\n\n"
        
        # Add requirements
        if job.requirements:
            combined_text += f"Requirements:\n{job.requirements}\n\n"
        
        # Add additional fields
        if job.title:
            combined_text += f"Job Title: {job.title}\n"
        if job.company:
            combined_text += f"Company: {job.company}\n"
        if job.location:
            combined_text += f"Location: {job.location}\n"
        if job.experience_level:
            combined_text += f"Experience Level: {job.experience_level}\n"
        if job.employment_type:
            combined_text += f"Employment Type: {job.employment_type}\n"
        
        # Extract and add PDF content if available
        if job.jd_pdf_path:
            pdf_text = JDPDFParser.extract_text(job.jd_pdf_path)
            if pdf_text:
                combined_text += f"\nAdditional Information from PDF:\n{pdf_text}\n"
        
        return combined_text.strip()
