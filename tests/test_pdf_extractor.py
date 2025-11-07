"""
Test PDF Extractor - Extract and Save Text from PDF Scripts
Saves extracted text to test-results/ directory for review
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_script_extractor import extract_pdf_text

def extract_and_save_script(pdf_path, output_dir="test-results"):
    """
    Extract text from PDF and save to text file
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save extracted text
    
    Returns:
        dict: Extraction result with file path
    """
    print(f"\nExtracting: {os.path.basename(pdf_path)}")
    print("-" * 80)
    
    # Extract text
    result = extract_pdf_text(pdf_path)
    
    if not result['success']:
        print(f"❌ Extraction failed: {result['error']}")
        return {
            "file": os.path.basename(pdf_path),
            "status": "FAILED",
            "error": result['error'],
            "timestamp": datetime.now().isoformat()
        }
    
    # Get metadata
    metadata = result['metadata']
    text = result['text']
    
    # Create output filename
    movie_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = os.path.join(output_dir, f"{movie_name}.txt")
    
    # Save extracted text
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"EXTRACTED TEXT FROM: {os.path.basename(pdf_path)}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Method: {metadata.get('method', 'unknown')}\n")
        f.write(f"Pages: {metadata.get('num_pages', 0)}\n")
        f.write(f"Words: {metadata.get('word_count', 0):,}\n")
        f.write(f"Characters: {metadata.get('char_count', 0):,}\n")
        f.write(f"File Size: {metadata.get('file_size', 0) / (1024*1024):.2f} MB\n")
        f.write("=" * 80 + "\n\n")
        f.write(text)
    
    print(f"✅ Extraction successful!")
    print(f"   Pages: {metadata.get('num_pages', 0)}")
    print(f"   Words: {metadata.get('word_count', 0):,}")
    print(f"   Characters: {metadata.get('char_count', 0):,}")
    print(f"   Method: {metadata.get('method', 'unknown')}")
    print(f"   Output: {output_file}")
    
    # Show preview of extracted text
    print(f"\n📖 Preview (first 500 characters):")
    print("-" * 80)
    print(text[:500])
    print("...")
    print("-" * 80)
    
    return {
        "file": os.path.basename(pdf_path),
        "status": "SUCCESS",
        "output_file": output_file,
        "pages": metadata.get('num_pages', 0),
        "words": metadata.get('word_count', 0),
        "characters": metadata.get('char_count', 0),
        "method": metadata.get('method', 'unknown'),
        "file_size_mb": metadata.get('file_size', 0) / (1024*1024),
        "preview": text[:500],
        "timestamp": datetime.now().isoformat()
    }

def review_extracted_content(text_file, lines=50):
    """
    Review the head of extracted content
    
    Args:
        text_file: Path to extracted text file
        lines: Number of lines to review
    
    Returns:
        dict: Review result
    """
    print(f"\n📄 Reviewing: {os.path.basename(text_file)}")
    print("-" * 80)
    
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()
        
        # Show first N lines
        head_content = ''.join(content_lines[:lines])
        
        print(f"First {lines} lines:")
        print("-" * 80)
        print(head_content)
        print("-" * 80)
        
        # Count lines and characters
        total_lines = len(content_lines)
        total_chars = sum(len(line) for line in content_lines)
        
        print(f"\n📊 File Statistics:")
        print(f"   Total Lines: {total_lines:,}")
        print(f"   Total Characters: {total_chars:,}")
        print(f"   Lines Reviewed: {min(lines, total_lines)}")
        
        return {
            "file": os.path.basename(text_file),
            "status": "SUCCESS",
            "total_lines": total_lines,
            "total_characters": total_chars,
            "lines_reviewed": min(lines, total_lines),
            "head_preview": head_content,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error reviewing file: {str(e)}")
        return {
            "file": os.path.basename(text_file),
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_extractor_tests():
    """Run PDF extractor tests on all PDF files in scripts directory"""
    print("=" * 80)
    print("PDF Extractor Test - Extract and Save Script Text")
    print("=" * 80)
    
    scripts_dir = "scripts"
    output_dir = "test-results"
    
    # Find all PDF files
    if not os.path.exists(scripts_dir):
        print(f"❌ Scripts directory not found: {scripts_dir}")
        return
    
    pdf_files = sorted([f for f in os.listdir(scripts_dir) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"❌ No PDF files found in {scripts_dir}")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s) to process:")
    for pdf in pdf_files:
        print(f"  - {pdf}")
    
    # Extract and save each PDF
    extraction_results = []
    review_results = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(scripts_dir, pdf_file)
        
        # Extract and save
        extract_result = extract_and_save_script(pdf_path, output_dir)
        extraction_results.append(extract_result)
        
        # Review extracted content if successful
        if extract_result['status'] == 'SUCCESS':
            review_result = review_extracted_content(extract_result['output_file'], lines=50)
            review_results.append(review_result)
    
    # Summary
    print("\n" + "=" * 80)
    print("Extraction Summary")
    print("=" * 80)
    
    successful = sum(1 for r in extraction_results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in extraction_results if r['status'] == 'FAILED')
    
    print(f"\nTotal PDFs: {len(pdf_files)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    if successful > 0:
        print(f"\n📁 Extracted text files saved to: {output_dir}/")
        for result in extraction_results:
            if result['status'] == 'SUCCESS':
                movie_name = os.path.splitext(result['file'])[0]
                print(f"   - {movie_name}.txt ({result['words']:,} words, {result['pages']} pages)")
    
    # Save test results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_output = os.path.join(output_dir, f"pdf_extractor_test_{timestamp}.json")
    
    test_data = {
        "test_suite": "PDF Extractor Test",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(pdf_files),
            "successful": successful,
            "failed": failed
        },
        "extraction_results": extraction_results,
        "review_results": review_results
    }
    
    with open(json_output, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n📊 Test results saved to: {json_output}")
    
    return test_data

if __name__ == "__main__":
    run_extractor_tests()
