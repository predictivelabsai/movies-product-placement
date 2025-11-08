#!/usr/bin/env python3
"""
Test Standardized Analysis Format
Tests the new standardized table format across different scripts
"""

import os
import sys
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_script_extractor import extract_pdf_text
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_analysis_template():
    """Load the standardized analysis template"""
    template_path = "prompts/standardized_analysis_template.txt"
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            return f.read()
    else:
        raise FileNotFoundError("Standardized analysis template not found")

def test_standardized_analysis(script_path, script_name):
    """Test standardized analysis on a single script"""
    print(f"\n{'='*80}")
    print(f"TESTING STANDARDIZED FORMAT: {script_name}")
    print(f"{'='*80}\n")
    
    # Extract text
    print("📖 Extracting script text...")
    result = extract_pdf_text(script_path)
    
    if not result['success']:
        print(f"❌ Failed to extract text: {result['error']}")
        return None
    
    script_text = result['text']
    print(f"✅ Extracted {result['metadata']['word_count']:,} words from {result['metadata']['num_pages']} pages")
    
    # Load template
    print("\n📋 Loading standardized analysis template...")
    try:
        analysis_template = load_analysis_template()
        print("✅ Template loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return None
    
    # Prepare script title
    script_title = script_name.replace('.pdf', '').replace('_', ' ')
    
    # Create analysis prompt
    analysis_prompt = f"""{analysis_template.replace('{SCRIPT_TITLE}', script_title)}

---

## SCREENPLAY EXCERPT TO ANALYZE:

{script_text[:15000]}

---

**IMPORTANT INSTRUCTIONS:**
- Follow the exact structure provided above
- Use markdown tables for all structured data
- Provide specific, actionable recommendations
- Include real brand names where appropriate
- Ensure all sections are comprehensive and detailed
- Focus on data consistency and professional formatting"""
    
    # Initialize Gemini 2.5 Flash (best for structured output)
    print("\n🤖 Initializing Google Gemini 2.5 Flash...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.5,
            max_output_tokens=4000
        )
        print("✅ Model initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        return None
    
    # Generate analysis
    print(f"\n🔍 Analyzing script with standardized format...")
    print(f"   Prompt length: {len(analysis_prompt):,} characters")
    print(f"   This may take 20-30 seconds...\n")
    
    try:
        response = llm.invoke(analysis_prompt)
        analysis = response.content
        print(f"✅ Analysis complete ({len(analysis):,} characters)")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test-results/{script_name.replace('.pdf', '')}_Standardized_{timestamp}.txt"
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"{script_title.upper()} - STANDARDIZED ANALYSIS FORMAT\n")
            f.write("="*80 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: gemini-2.0-flash-exp\n")
            f.write(f"Template: Standardized Table Format\n")
            f.write(f"Analysis Length: {len(analysis):,} characters\n")
            f.write("="*80 + "\n\n")
            f.write(analysis)
        
        print(f"💾 Saved to: {output_file}")
        
        # Show preview
        print(f"\n📄 Analysis preview (first 800 characters):")
        print("-" * 80)
        print(analysis[:800])
        print("-" * 80)
        
        return {
            "success": True,
            "script": script_name,
            "analysis_length": len(analysis),
            "output_file": output_file,
            "preview": analysis[:800]
        }
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return {
            "success": False,
            "script": script_name,
            "error": str(e)
        }

def main():
    """Run standardized format tests on all available scripts"""
    print("="*80)
    print("STANDARDIZED ANALYSIS FORMAT TEST SUITE")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    # Get all scripts
    scripts_dir = "scripts"
    if not os.path.exists(scripts_dir):
        print(f"❌ Scripts directory not found: {scripts_dir}")
        return
    
    pdf_files = [f for f in os.listdir(scripts_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in {scripts_dir}")
        return
    
    print(f"\n📚 Found {len(pdf_files)} scripts to test:")
    for i, script in enumerate(pdf_files, 1):
        print(f"   {i}. {script}")
    
    # Test each script
    results = []
    for script in pdf_files:
        script_path = os.path.join(scripts_dir, script)
        result = test_standardized_analysis(script_path, script)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"📄 Total Scripts: {len(pdf_files)}")
    print(f"✅ Successful: {sum(1 for r in results if r['success'])}")
    print(f"❌ Failed: {sum(1 for r in results if not r['success'])}")
    print(f"Success Rate: {sum(1 for r in results if r['success'])/len(results)*100:.1f}%")
    
    print(f"\n📊 Analysis Details:")
    for result in results:
        if result['success']:
            print(f"\n{result['script']}: ✅ PASSED")
            print(f"   Analysis Length: {result['analysis_length']:,} characters")
            print(f"   Output File: {result['output_file']}")
        else:
            print(f"\n{result['script']}: ❌ FAILED")
            print(f"   Error: {result['error']}")
    
    # Save summary JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"test-results/standardized_format_test_{timestamp}.json"
    
    with open(summary_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_scripts": len(pdf_files),
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {summary_file}")
    print("="*80)

if __name__ == "__main__":
    main()
