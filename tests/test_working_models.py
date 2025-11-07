#!/usr/bin/env python3
"""
Test Working AI Models
Tests only the models that are actually available and working
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

def test_google_gemini_2_flash():
    """Test Google Gemini 2.0 Flash model (via Google API)"""
    print("\n" + "="*80)
    print("Testing Google Gemini 2.0 Flash (Default)")
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
            max_output_tokens=1000
        )
        
        print("✅ ChatGoogleGenerativeAI initialized successfully")
        
        test_prompt = "List 3 product placement opportunities in a coffee shop scene."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:400])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gemini-2.0-flash-exp",
            "provider": "google",
            "response_length": len(result),
            "response_preview": result[:400]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_gemini_25_flash():
    """Test Gemini 2.5 Flash (via OpenAI-compatible API)"""
    print("\n" + "="*80)
    print("Testing Google Gemini 2.5 Flash (OpenAI API)")
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
            max_tokens=1000
        )
        
        print("✅ ChatOpenAI initialized successfully")
        
        test_prompt = "List 3 product placement opportunities in a tech startup scene."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:400])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gemini-2.5-flash",
            "provider": "openai",
            "response_length": len(result),
            "response_preview": result[:400]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_gpt41_mini():
    """Test GPT-4.1 Mini model"""
    print("\n" + "="*80)
    print("Testing OpenAI GPT-4.1 Mini")
    print("="*80)
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"success": False, "error": "OPENAI_API_KEY not found"}
        
        print(f"✅ OpenAI API key found")
        
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            api_key=api_key,
            temperature=0.5,
            max_tokens=1000
        )
        
        print("✅ ChatOpenAI initialized successfully")
        
        test_prompt = "List 3 product placement opportunities in a romantic comedy."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:400])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "gpt-4.1-mini",
            "provider": "openai",
            "response_length": len(result),
            "response_preview": result[:400]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_xai_grok3():
    """Test XAI Grok 3 model"""
    print("\n" + "="*80)
    print("Testing XAI Grok 3")
    print("="*80)
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            return {"success": False, "error": "XAI_API_KEY not found"}
        
        print(f"✅ XAI API key found")
        
        llm = ChatOpenAI(
            model="grok-3",
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=0.5,
            max_tokens=1000
        )
        
        print("✅ ChatOpenAI (XAI) initialized successfully")
        
        test_prompt = "List 3 product placement opportunities in a sci-fi movie."
        
        print("\n📝 Sending test prompt...")
        response = llm.invoke(test_prompt)
        result = response.content
        
        print(f"\n✅ Response received ({len(result)} characters)")
        print("\n📄 Response preview:")
        print("-" * 80)
        print(result[:400])
        print("-" * 80)
        
        return {
            "success": True,
            "model": "grok-3",
            "provider": "xai",
            "response_length": len(result),
            "response_preview": result[:400]
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Run all working model tests"""
    print("\n" + "="*80)
    print("Working AI Models Test Suite")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "test_date": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test Google Gemini 2.0 Flash (default)
    results["tests"]["google_gemini_2_flash"] = test_google_gemini_2_flash()
    
    # Test Gemini 2.5 Flash (via OpenAI API)
    results["tests"]["gemini_25_flash"] = test_gemini_25_flash()
    
    # Test GPT-4.1 Mini
    results["tests"]["gpt41_mini"] = test_gpt41_mini()
    
    # Test XAI Grok 3
    results["tests"]["xai_grok3"] = test_xai_grok3()
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    total_tests = len(results["tests"])
    successful_tests = sum(1 for test in results["tests"].values() if test.get("success"))
    
    for test_name, test_result in results["tests"].items():
        status = "✅ PASSED" if test_result.get("success") else "❌ FAILED"
        model = test_result.get("model", "unknown")
        provider = test_result.get("provider", "unknown")
        print(f"{test_name} ({provider}/{model}): {status}")
        if not test_result.get("success"):
            print(f"  Error: {test_result.get('error')}")
    
    print(f"\nTotal: {successful_tests}/{total_tests} tests passed")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Save results
    os.makedirs("test-results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test-results/working_models_test_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
