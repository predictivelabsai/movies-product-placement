"""
PDF Script Extractor Utility
Extracts text content from PDF screenplay files for analysis
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class PDFScriptExtractor:
    """
    Extract text from PDF screenplay files using multiple methods
    """
    
    def __init__(self):
        """Initialize the PDF extractor"""
        self.methods_available = {
            'pypdf2': PYPDF2_AVAILABLE,
            'ocr': OCR_AVAILABLE
        }
    
    def extract_text(self, pdf_path: str, method: str = 'auto') -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method ('auto', 'pypdf2', 'ocr')
        
        Returns:
            dict: Extraction result with text, metadata, and status
        """
        if not os.path.exists(pdf_path):
            return {
                'success': False,
                'error': f'File not found: {pdf_path}',
                'text': '',
                'metadata': {}
            }
        
        # Auto-select method
        if method == 'auto':
            if PYPDF2_AVAILABLE:
                method = 'pypdf2'
            elif OCR_AVAILABLE:
                method = 'ocr'
            else:
                return {
                    'success': False,
                    'error': 'No PDF extraction libraries available. Install PyPDF2 or pdf2image+pytesseract',
                    'text': '',
                    'metadata': {}
                }
        
        # Extract using selected method
        if method == 'pypdf2':
            return self._extract_with_pypdf2(pdf_path)
        elif method == 'ocr':
            return self._extract_with_ocr(pdf_path)
        else:
            return {
                'success': False,
                'error': f'Unknown extraction method: {method}',
                'text': '',
                'metadata': {}
            }
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text using PyPDF2
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            dict: Extraction result
        """
        if not PYPDF2_AVAILABLE:
            return {
                'success': False,
                'error': 'PyPDF2 not installed',
                'text': '',
                'metadata': {}
            }
        
        try:
            text_content = []
            metadata = {}
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'method': 'pypdf2',
                    'file_name': os.path.basename(pdf_path),
                    'file_size': os.path.getsize(pdf_path)
                }
                
                # Try to get PDF metadata
                if pdf_reader.metadata:
                    try:
                        metadata['title'] = pdf_reader.metadata.get('/Title', '')
                        metadata['author'] = pdf_reader.metadata.get('/Author', '')
                        metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                    except:
                        pass
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num}: {str(e)}")
            
            full_text = '\n\n'.join(text_content)
            
            if not full_text.strip():
                return {
                    'success': False,
                    'error': 'No text could be extracted. PDF may be image-based or encrypted.',
                    'text': '',
                    'metadata': metadata
                }
            
            metadata['char_count'] = len(full_text)
            metadata['word_count'] = len(full_text.split())
            
            return {
                'success': True,
                'text': full_text,
                'metadata': metadata,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error extracting PDF: {str(e)}',
                'text': '',
                'metadata': {}
            }
    
    def _extract_with_ocr(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text using OCR (for image-based PDFs)
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            dict: Extraction result
        """
        if not OCR_AVAILABLE:
            return {
                'success': False,
                'error': 'OCR libraries not installed (pdf2image, pytesseract)',
                'text': '',
                'metadata': {}
            }
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            text_content = []
            metadata = {
                'num_pages': len(images),
                'method': 'ocr',
                'file_name': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path)
            }
            
            # Extract text from each image using OCR
            for page_num, image in enumerate(images, 1):
                try:
                    page_text = pytesseract.image_to_string(image)
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    print(f"Warning: Could not OCR page {page_num}: {str(e)}")
            
            full_text = '\n\n'.join(text_content)
            
            if not full_text.strip():
                return {
                    'success': False,
                    'error': 'No text could be extracted via OCR',
                    'text': '',
                    'metadata': metadata
                }
            
            metadata['char_count'] = len(full_text)
            metadata['word_count'] = len(full_text.split())
            
            return {
                'success': True,
                'text': full_text,
                'metadata': metadata,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error during OCR extraction: {str(e)}',
                'text': '',
                'metadata': {}
            }
    
    def get_available_methods(self) -> Dict[str, bool]:
        """
        Get available extraction methods
        
        Returns:
            dict: Available methods and their status
        """
        return self.methods_available.copy()
    
    def extract_text_simple(self, pdf_path: str) -> str:
        """
        Simple text extraction (returns only text, no metadata)
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            str: Extracted text or empty string on error
        """
        result = self.extract_text(pdf_path)
        return result.get('text', '')


def extract_pdf_text(pdf_path: str, method: str = 'auto') -> Dict[str, Any]:
    """
    Convenience function to extract text from PDF
    
    Args:
        pdf_path: Path to PDF file
        method: Extraction method ('auto', 'pypdf2', 'ocr')
    
    Returns:
        dict: Extraction result
    """
    extractor = PDFScriptExtractor()
    return extractor.extract_text(pdf_path, method)


def extract_pdf_text_simple(pdf_path: str) -> str:
    """
    Convenience function to extract text from PDF (simple)
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        str: Extracted text
    """
    extractor = PDFScriptExtractor()
    return extractor.extract_text_simple(pdf_path)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_script_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    print(f"Extracting text from: {pdf_file}")
    print("-" * 80)
    
    result = extract_pdf_text(pdf_file)
    
    if result['success']:
        print(f"✅ Extraction successful!")
        print(f"\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
        
        print(f"\nText preview (first 500 characters):")
        print(result['text'][:500])
        print("...")
    else:
        print(f"❌ Extraction failed: {result['error']}")
