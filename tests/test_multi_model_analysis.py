#!/usr/bin/env python3
"""
Test Multi-Model AI Analysis
Tests script analysis with Google Gemini, OpenAI, and XAI models
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def test_google_gemini_flash():
    """Test Google Gemini 2.0 Flash model"""
    print("\n" + "="*80)
    print("Testing Google Gemini 2.0 Flash")
    print("="*80)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"success": False, "error": "GOOGLE_API_KEY not found"}
        
        print(f"✅ Google API key found: {api_key[:20]}...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.5,
            max_output_tokens=1000
        )
        
        print("✅ ChatGoogleGenerativeAI initialized successfully")
        
        test_prompt = """Analyze this short movie scene for product placement opportunities:

SCENE: Coffee Shop - Morning
SARAH sits at a table with her laptop, sipping coffee. Her phone buzzes.

SARAH
(answering)
Hey! Yeah, I'm at the cafe. Just finishing up some work.

She types on her laptop while talking, occasionally glancing at her smartwatch.

Provide 3 product placement opportunities from this scene."""
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:500])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gemini-2.0-flash-exp",
            "provider": "google",
            "response_length": len(result),
            "response_preview": result[:500]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_google_gemini_pro():
    """Test Google Gemini 1.5 Pro model"""
    print("\n" + "="*80)
    print("Testing Google Gemini 1.5 Pro")
    print("="*80)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"success": False, "error": "GOOGLE_API_KEY not found"}
        
        print(f"✅ Google API key found")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.5,
            max_output_tokens=1000
        )
        
        print("✅ ChatGoogleGenerativeAI initialized successfully")
        
        test_prompt = "List 3 popular product placement opportunities in action movies."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:300])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gemini-1.5-pro",
            "provider": "google",
            "response_length": len(result),
            "response_preview": result[:300]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_openai_gpt4():
    """Test OpenAI GPT-4 model"""
    print("\n" + "="*80)
    print("Testing OpenAI GPT-4")
    print("="*80)
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"success": False, "error": "OPENAI_API_KEY not found"}
        
        print(f"✅ OpenAI API key found: {api_key[:20]}...")
        
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=api_key,
            temperature=0.5,
            max_tokens=1000
        )
        
        print("✅ ChatOpenAI initialized successfully")
        
        test_prompt = "List 3 popular product placement opportunities in romantic comedies."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:300])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gpt-4",
            "provider": "openai",
            "response_length": len(result),
            "response_preview": result[:300]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_xai_grok():
    """Test XAI Grok model"""
    print("\n" + "="*80)
    print("Testing XAI Grok Beta")
    print("="*80)
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            return {"success": False, "error": "XAI_API_KEY not found"}
        
        print(f"✅ XAI API key found: {api_key[:20]}...")
        
        llm = ChatOpenAI(
            model="grok-beta",
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=0.5,
            max_tokens=1000
        )
        
        print("✅ ChatOpenAI (XAI) initialized successfully")
        
        test_prompt = "List 3 popular product placement opportunities in sci-fi movies."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:300])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "grok-beta",
            "provider": "xai",
            "response_length": len(result),
            "response_preview": result[:300]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Run all multi-model tests"""
    print("\n" + "="*80)
    print("Multi-Model AI Analysis Test Suite")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "test_date": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test Google Gemini Flash (default)
    results["tests"]["google_gemini_flash"] = test_google_gemini_flash()
    
    # Test Google Gemini Pro
    results["tests"]["google_gemini_pro"] = test_google_gemini_pro()
    
    # Test OpenAI GPT-4
    results["tests"]["openai_gpt4"] = test_openai_gpt4()
    
    # Test XAI Grok
    results["tests"]["xai_grok"] = test_xai_grok()
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    total_tests = len(results["tests"])
    successful_tests = sum(1 for test in results["tests"].values() if test.get("success"))
    
    for test_name, test_result in results["tests"].items():
        status = "✅ PASSED" if test_result.get("success") else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not test_result.get("success"):
            print(f"  Error: {test_result.get('error')}")
    
    print(f"\nTotal: {successful_tests}/{total_tests} tests passed")
    
    # Save results
    os.makedirs("test-results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test-results/multi_model_tests_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
