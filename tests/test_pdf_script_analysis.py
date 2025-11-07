"""
Test PDF Script Analysis
Tests PDF extraction and script analysis functionality
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_script_extractor import extract_pdf_text, PDFScriptExtractor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pdf_extractor_initialization():
    """Test PDF extractor can be initialized"""
    print("Testing PDF extractor initialization...")
    
    try:
        extractor = PDFScriptExtractor()
        available_methods = extractor.get_available_methods()
        
        return {
            "test": "PDF Extractor Initialization",
            "status": "SUCCESS",
            "available_methods": available_methods,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test": "PDF Extractor Initialization",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_pdf_text_extraction():
    """Test PDF text extraction on sample scripts"""
    print("Testing PDF text extraction...")
    
    try:
        # Find PDF files in scripts directory
        scripts_dir = "scripts"
        pdf_files = [f for f in os.listdir(scripts_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            return {
                "test": "PDF Text Extraction",
                "status": "WARNING",
                "message": "No PDF files found in scripts directory",
                "timestamp": datetime.now().isoformat()
            }
        
        # Test extraction on first PDF
        test_pdf = os.path.join(scripts_dir, pdf_files[0])
        result = extract_pdf_text(test_pdf)
        
        if result['success']:
            metadata = result['metadata']
            text_preview = result['text'][:200] if result['text'] else ""
            
            return {
                "test": "PDF Text Extraction",
                "status": "SUCCESS",
                "pdf_file": pdf_files[0],
                "pages": metadata.get('num_pages', 0),
                "words": metadata.get('word_count', 0),
                "characters": metadata.get('char_count', 0),
                "method": metadata.get('method', 'unknown'),
                "text_preview": text_preview,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "test": "PDF Text Extraction",
                "status": "FAILED",
                "error": result.get('error', 'Unknown error'),
                "pdf_file": pdf_files[0],
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {
            "test": "PDF Text Extraction",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_multiple_pdf_extraction():
    """Test extraction on multiple PDF files"""
    print("Testing multiple PDF extraction...")
    
    try:
        scripts_dir = "scripts"
        pdf_files = [f for f in os.listdir(scripts_dir) if f.endswith('.pdf')]
        
        if len(pdf_files) < 2:
            return {
                "test": "Multiple PDF Extraction",
                "status": "WARNING",
                "message": f"Only {len(pdf_files)} PDF file(s) found, need at least 2",
                "timestamp": datetime.now().isoformat()
            }
        
        results = []
        for pdf_file in pdf_files[:2]:  # Test first 2 PDFs
            pdf_path = os.path.join(scripts_dir, pdf_file)
            result = extract_pdf_text(pdf_path)
            
            results.append({
                'file': pdf_file,
                'success': result['success'],
                'pages': result['metadata'].get('num_pages', 0) if result['success'] else 0,
                'words': result['metadata'].get('word_count', 0) if result['success'] else 0
            })
        
        all_success = all(r['success'] for r in results)
        
        return {
            "test": "Multiple PDF Extraction",
            "status": "SUCCESS" if all_success else "FAILED",
            "files_tested": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test": "Multiple PDF Extraction",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_ai_script_analysis():
    """Test AI analysis on extracted PDF text"""
    print("Testing AI script analysis...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "test": "AI Script Analysis",
                "status": "WARNING",
                "message": "OpenAI API key not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Find a PDF to analyze
        scripts_dir = "scripts"
        pdf_files = [f for f in os.listdir(scripts_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            return {
                "test": "AI Script Analysis",
                "status": "WARNING",
                "message": "No PDF files found for analysis",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract text from first PDF
        test_pdf = os.path.join(scripts_dir, pdf_files[0])
        extraction_result = extract_pdf_text(test_pdf)
        
        if not extraction_result['success']:
            return {
                "test": "AI Script Analysis",
                "status": "FAILED",
                "error": f"Failed to extract PDF: {extraction_result.get('error')}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Initialize LLM with Gemini 2.5 Flash
        llm = ChatOpenAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=1000
        )
        
        # Create analysis prompt (use first 3000 characters)
        script_text = extraction_result['text'][:3000]
        analysis_prompt = f"""Analyze this movie script excerpt and identify:
1. Main characters
2. Setting/location
3. Genre
4. One product placement opportunity

Script excerpt:
{script_text}

Provide a brief analysis (max 200 words)."""
        
        # Generate analysis
        response = llm.invoke(analysis_prompt)
        analysis_result = response.content
        
        return {
            "test": "AI Script Analysis",
            "status": "SUCCESS",
            "pdf_file": pdf_files[0],
            "model": "gemini-2.5-flash",
            "script_excerpt_length": len(script_text),
            "analysis_length": len(analysis_result),
            "analysis_preview": analysis_result[:300],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test": "AI Script Analysis",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_all_tests():
    """Run all PDF script analysis tests"""
    print("="*80)
    print("Vadis Media Product Placement - PDF Script Analysis Tests")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(test_pdf_extractor_initialization())
    results.append(test_pdf_text_extraction())
    results.append(test_multiple_pdf_extraction())
    results.append(test_ai_script_analysis())
    
    # Calculate summary
    summary = {
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == "SUCCESS"),
        "failed": sum(1 for r in results if r["status"] == "FAILED"),
        "warning": sum(1 for r in results if r["status"] == "WARNING")
    }
    
    # Print results
    print("="*80)
    print("Test Summary")
    print("="*80)
    
    for result in results:
        status_emoji = {
            "SUCCESS": "✅",
            "FAILED": "❌",
            "WARNING": "⚠️"
        }.get(result["status"], "❓")
        
        print(f"{status_emoji} {result['test']}: {result['status']}")
    
    print(f"\nTotal: {summary['total']} | Success: {summary['success']} | Failed: {summary['failed']} | Warning: {summary['warning']}")
    
    # Save results to JSON
    os.makedirs("test-results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test-results/pdf_script_analysis_tests_{timestamp}.json"
    
    test_data = {
        "test_suite": "PDF Script Analysis Tests",
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "results": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return test_data

if __name__ == "__main__":
    run_all_tests()
