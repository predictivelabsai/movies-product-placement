#!/usr/bin/env python3
"""
Test script to verify the ChatOpenAI fix works correctly
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

def test_script_generation():
    """Test the script generation with the new invoke method"""
    
    print("🧪 Testing ChatOpenAI with gpt-4.1-mini and invoke method...")
    
    # Check if API key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return False
    
    try:
        # Initialize LLM with gpt-4.1-mini
        print("📝 Initializing ChatOpenAI with gpt-4.1-mini...")
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.7,
            max_tokens=500  # Keep it short for testing
        )
        print("✅ ChatOpenAI initialized successfully")
        
        # Create a simple prompt template
        prompt_template = PromptTemplate(
            input_variables=["genre", "target_audience", "setting"],
            template="""You are a professional screenwriter. Generate a brief script outline for a {genre} movie.

Genre: {genre}
Target audience: {target_audience}
Setting: {setting}

Provide a short outline with:
1. Title
2. Logline (one sentence)
3. Three main characters
4. Brief plot summary (3-4 sentences)
"""
        )
        
        # Format the prompt
        print("📋 Formatting prompt...")
        formatted_prompt = prompt_template.format(
            genre="Thriller",
            target_audience="Adult (R)",
            setting="Modern urban city"
        )
        print("✅ Prompt formatted successfully")
        
        # Test the invoke method
        print("🚀 Invoking LLM with formatted prompt...")
        response = llm.invoke(formatted_prompt)
        result = response.content
        print("✅ LLM invoked successfully")
        
        # Display result
        print("\n" + "="*80)
        print("📄 GENERATED SCRIPT OUTLINE:")
        print("="*80)
        print(result)
        print("="*80)
        
        print("\n✅ TEST PASSED: Script generation is working correctly!")
        return True
        
    except AttributeError as e:
        print(f"\n❌ TEST FAILED: AttributeError - {str(e)}")
        print("This suggests the method name is still incorrect")
        return False
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {type(e).__name__} - {str(e)}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("TESTING SCRIPT GENERATION FIX")
    print("="*80)
    print()
    
    success = test_script_generation()
    
    print()
    print("="*80)
    if success:
        print("✅ ALL TESTS PASSED - The fix is working correctly!")
        print("You can now use the AI Script Generation page in the Streamlit app.")
    else:
        print("❌ TESTS FAILED - Please check the error messages above")
    print("="*80)
