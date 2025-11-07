#!/usr/bin/env python3
"""
Test The Avengers Script Analysis with Google Gemini Models
Tests both Gemini 2.0 Flash and Gemini 2.5 Flash
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_script_extractor import PDFScriptExtractor

# Load environment variables
load_dotenv()

def extract_avengers_script():
    """Extract The Avengers script"""
    print("\n" + "="*80)
    print("Extracting The Avengers Script")
    print("="*80)
    
    extractor = PDFScriptExtractor()
    result = extractor.extract_text('scripts/The_Avengers.pdf')
    
    if result['success']:
        print(f"✅ Extraction successful!")
        print(f"   Pages: {result['metadata']['num_pages']}")
        print(f"   Words: {result['metadata']['word_count']:,}")
        print(f"   Characters: {result['metadata']['char_count']:,}")
        
        # Save extracted text
        os.makedirs("test-results", exist_ok=True)
        output_file = "test-results/The_Avengers_extracted.txt"
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("THE AVENGERS - EXTRACTED TEXT\n")
            f.write("="*80 + "\n")
            f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Pages: {result['metadata']['num_pages']}\n")
            f.write(f"Words: {result['metadata']['word_count']:,}\n")
            f.write(f"Characters: {result['metadata']['char_count']:,}\n")
            f.write("="*80 + "\n\n")
            f.write(result['text'])
        
        print(f"   Saved to: {output_file}")
        
        return result
    else:
        print(f"❌ Error: {result['error']}")
        return None

def test_gemini_2_flash(script_text):
    """Test Google Gemini 2.0 Flash analysis"""
    print("\n" + "="*80)
    print("Testing Google Gemini 2.0 Flash Analysis")
    print("="*80)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"success": False, "error": "GOOGLE_API_KEY not found"}
        
        print(f"✅ Google API key found")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.5,
            max_output_tokens=4000
        )
        
        print("✅ ChatGoogleGenerativeAI initialized successfully")
        
        # Use first 15,000 characters for analysis
        script_sample = script_text[:15000]
        
        analysis_prompt = f"""You are an expert screenplay analyst specializing in product placement opportunities and market analysis.

Analyze the following excerpt from THE AVENGERS movie script and provide a detailed analysis covering:

1. **Product Placement Opportunities**: Identify 5-7 specific scenes or moments where products could be naturally integrated
2. **Market Potential**: Assess the commercial appeal and target demographics
3. **Character Analysis**: Brief overview of main characters and their lifestyle/preferences
4. **Scene Breakdown**: Highlight key scenes suitable for product integration

Script Excerpt (first 15,000 characters):
{script_sample}

Provide specific examples with scene descriptions and actionable recommendations."""
        
        print(f"\n📝 Sending analysis prompt ({len(analysis_prompt)} characters)...")
        print("⏳ This may take 10-20 seconds...")
        
        response = llm.invoke(analysis_prompt)
        result = response.content
        
        print(f"\n✅ Analysis received ({len(result)} characters)")
        
        # Save analysis
        os.makedirs("test-results", exist_ok=True)
        output_file = f"test-results/The_Avengers_Gemini_2_Flash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("THE AVENGERS - GOOGLE GEMINI 2.0 FLASH ANALYSIS\n")
            f.write("="*80 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: gemini-2.0-flash-exp\n")
            f.write(f"Temperature: 0.5\n")
            f.write(f"Analysis Length: {len(result):,} characters\n")
            f.write("="*80 + "\n\n")
            f.write(result)
        
        print(f"   Saved to: {output_file}")
        
        print("\n📄 Analysis preview (first 800 characters):")
        print("-" * 80)
        print(result[:800])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gemini-2.0-flash-exp",
            "provider": "google",
            "analysis_length": len(result),
            "output_file": output_file,
            "preview": result[:800]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_gemini_25_flash(script_text):
    """Test Google Gemini 2.5 Flash analysis (via OpenAI API)"""
    print("\n" + "="*80)
    print("Testing Google Gemini 2.5 Flash Analysis")
    print("="*80)
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"success": False, "error": "OPENAI_API_KEY not found"}
        
        print(f"✅ OpenAI API key found")
        
        llm = ChatOpenAI(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0.5,
            max_tokens=4000
        )
        
        print("✅ ChatOpenAI (Gemini 2.5 Flash) initialized successfully")
        
        # Use first 15,000 characters for analysis
        script_sample = script_text[:15000]
        
        analysis_prompt = f"""You are an expert screenplay analyst specializing in product placement opportunities and market analysis.

Analyze the following excerpt from THE AVENGERS movie script and provide a detailed analysis covering:

1. **Product Placement Opportunities**: Identify 5-7 specific scenes or moments where products could be naturally integrated
2. **Market Potential**: Assess the commercial appeal and target demographics
3. **Character Analysis**: Brief overview of main characters and their lifestyle/preferences
4. **Scene Breakdown**: Highlight key scenes suitable for product integration

Script Excerpt (first 15,000 characters):
{script_sample}

Provide specific examples with scene descriptions and actionable recommendations."""
        
        print(f"\n📝 Sending analysis prompt ({len(analysis_prompt)} characters)...")
        print("⏳ This may take 10-20 seconds...")
        
        response = llm.invoke(analysis_prompt)
        result = response.content
        
        print(f"\n✅ Analysis received ({len(result)} characters)")
        
        # Save analysis
        os.makedirs("test-results", exist_ok=True)
        output_file = f"test-results/The_Avengers_Gemini_25_Flash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("THE AVENGERS - GOOGLE GEMINI 2.5 FLASH ANALYSIS\n")
            f.write("="*80 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: gemini-2.5-flash\n")
            f.write(f"Temperature: 0.5\n")
            f.write(f"Analysis Length: {len(result):,} characters\n")
            f.write("="*80 + "\n\n")
            f.write(result)
        
        print(f"   Saved to: {output_file}")
        
        print("\n📄 Analysis preview (first 800 characters):")
        print("-" * 80)
        print(result[:800])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gemini-2.5-flash",
            "provider": "openai",
            "analysis_length": len(result),
            "output_file": output_file,
            "preview": result[:800]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Run The Avengers analysis tests"""
    print("\n" + "="*80)
    print("THE AVENGERS - GOOGLE GEMINI ANALYSIS TEST SUITE")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "test_date": datetime.now().isoformat(),
        "script": "The_Avengers.pdf",
        "tests": {}
    }
    
    # Extract script
    extraction_result = extract_avengers_script()
    if not extraction_result:
        print("\n❌ Script extraction failed. Aborting tests.")
        return
    
    script_text = extraction_result['text']
    results["extraction"] = {
        "success": True,
        "pages": extraction_result['metadata']['num_pages'],
        "words": extraction_result['metadata']['word_count'],
        "characters": extraction_result['metadata']['char_count']
    }
    
    # Test Gemini 2.0 Flash
    results["tests"]["gemini_2_flash"] = test_gemini_2_flash(script_text)
    
    # Test Gemini 2.5 Flash
    results["tests"]["gemini_25_flash"] = test_gemini_25_flash(script_text)
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    print(f"\n📄 Script: The_Avengers.pdf")
    print(f"   Pages: {results['extraction']['pages']}")
    print(f"   Words: {results['extraction']['words']:,}")
    print(f"   Characters: {results['extraction']['characters']:,}")
    
    print(f"\n🤖 AI Model Tests:")
    total_tests = len(results["tests"])
    successful_tests = sum(1 for test in results["tests"].values() if test.get("success"))
    
    for test_name, test_result in results["tests"].items():
        status = "✅ PASSED" if test_result.get("success") else "❌ FAILED"
        model = test_result.get("model", "unknown")
        provider = test_result.get("provider", "unknown")
        analysis_len = test_result.get("analysis_length", 0)
        
        print(f"\n{test_name} ({provider}/{model}): {status}")
        if test_result.get("success"):
            print(f"   Analysis Length: {analysis_len:,} characters")
            print(f"   Output File: {test_result.get('output_file')}")
        else:
            print(f"   Error: {test_result.get('error')}")
    
    print(f"\n📊 Total: {successful_tests}/{total_tests} tests passed")
    print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Save results JSON
    os.makedirs("test-results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_output = f"test-results/avengers_gemini_test_{timestamp}.json"
    
    with open(json_output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {json_output}")
    
    return results

if __name__ == "__main__":
    main()
