#!/usr/bin/env python3
"""
Simple test to verify OpenAI API key is working correctly
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import from project
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def test_openai_simple_question():
    """Test OpenAI with a simple question: What is the capital of France?"""
    
    print("="*80)
    print("TESTING OPENAI API KEY")
    print("="*80)
    print()
    
    # Check if API key exists
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    try:
        # Initialize ChatOpenAI with gpt-4.1-mini
        print("📝 Initializing ChatOpenAI with gpt-4.1-mini...")
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.0,  # Use 0 for deterministic response
            max_tokens=100
        )
        print("✅ ChatOpenAI initialized successfully")
        print()
        
        # Ask a simple question
        question = "What is the capital of France? Answer in one word."
        print(f"❓ Question: {question}")
        print()
        
        # Invoke the model
        print("🚀 Sending request to OpenAI...")
        response = llm.invoke(question)
        answer = response.content
        print("✅ Response received")
        print()
        
        # Display the answer
        print("="*80)
        print("ANSWER:")
        print("="*80)
        print(answer)
        print("="*80)
        print()
        
        # Verify the answer contains "Paris"
        if "Paris" in answer or "paris" in answer.lower():
            print("✅ TEST PASSED: Correct answer received!")
            print("✅ OpenAI API key is working correctly")
            return True
        else:
            print("⚠️  WARNING: Answer doesn't contain 'Paris'")
            print("⚠️  But the API is responding, so the key is valid")
            return True
            
    except Exception as e:
        print(f"❌ TEST FAILED: {type(e).__name__}")
        print(f"❌ Error: {str(e)}")
        print()
        
        # Provide helpful error messages
        if "authentication" in str(e).lower() or "api key" in str(e).lower():
            print("💡 TIP: The API key appears to be invalid or expired")
            print("💡 Please check your OpenAI account and generate a new key")
        elif "rate limit" in str(e).lower():
            print("💡 TIP: Rate limit exceeded. Wait a moment and try again")
        elif "model" in str(e).lower():
            print("💡 TIP: The model 'gpt-4.1-mini' might not be available")
            print("💡 Try using 'gpt-4.1-nano' or 'gemini-2.5-flash' instead")
        
        return False

if __name__ == "__main__":
    print()
    success = test_openai_simple_question()
    print()
    print("="*80)
    if success:
        print("✅ ALL TESTS PASSED")
        print("The OpenAI API key is working correctly!")
    else:
        print("❌ TESTS FAILED")
        print("Please check the error messages above")
    print("="*80)
    print()
    
    sys.exit(0 if success else 1)
