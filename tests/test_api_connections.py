"""
Test API connections for Vadis Media Product Placement Platform
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    print("Testing OpenAI API...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "api": "OpenAI",
                "status": "FAILED",
                "error": "API key not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        llm = ChatOpenAI(model="gpt-4", temperature=0.7, max_tokens=50)
        result = llm.predict("Say 'API test successful' in one sentence.")
        
        return {
            "api": "OpenAI",
            "status": "SUCCESS",
            "response": result[:100],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "api": "OpenAI",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_tmdb_connection():
    """Test TMDB API connection"""
    print("Testing TMDB API...")
    
    try:
        from tmdbv3api import TMDb, Person
        
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            return {
                "api": "TMDB",
                "status": "FAILED",
                "error": "API key not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        tmdb = TMDb()
        tmdb.api_key = api_key
        tmdb.language = 'en'
        
        person = Person()
        results = person.popular()
        
        return {
            "api": "TMDB",
            "status": "SUCCESS",
            "results_count": len(results) if results else 0,
            "sample": results[0].name if results and len(results) > 0 else "N/A",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "api": "TMDB",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_omdb_connection():
    """Test OMDB API connection"""
    print("Testing OMDB API...")
    
    try:
        import requests
        
        api_key = os.getenv("OMDB_API_KEY")
        if not api_key:
            return {
                "api": "OMDB",
                "status": "FAILED",
                "error": "API key not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        url = f"http://www.omdbapi.com/?apikey={api_key}&t=Inception"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    "api": "OMDB",
                    "status": "SUCCESS",
                    "sample": f"{data.get('Title')} ({data.get('Year')})",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "api": "OMDB",
                    "status": "FAILED",
                    "error": data.get('Error'),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "api": "OMDB",
                "status": "FAILED",
                "error": f"HTTP {response.status_code}",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {
            "api": "OMDB",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_tavily_connection():
    """Test Tavily API connection"""
    print("Testing Tavily API...")
    
    try:
        from tavily import TavilyClient
        
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return {
                "api": "Tavily",
                "status": "FAILED",
                "error": "API key not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        client = TavilyClient(api_key=api_key)
        response = client.search("movie industry trends", max_results=1)
        
        if response and 'results' in response:
            return {
                "api": "Tavily",
                "status": "SUCCESS",
                "results_count": len(response['results']),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "api": "Tavily",
                "status": "WARNING",
                "message": "Connected but no results",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {
            "api": "Tavily",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_all_tests():
    """Run all API connection tests"""
    print("="*80)
    print("Vadis Media Product Placement - API Connection Tests")
    print("="*80)
    print()
    
    results = []
    
    # Test each API
    results.append(test_openai_connection())
    results.append(test_tmdb_connection())
    results.append(test_omdb_connection())
    results.append(test_tavily_connection())
    
    # Summary
    print()
    print("="*80)
    print("Test Summary")
    print("="*80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    warning_count = sum(1 for r in results if r['status'] == 'WARNING')
    
    for result in results:
        status_symbol = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "⚠️"
        print(f"{status_symbol} {result['api']}: {result['status']}")
    
    print()
    print(f"Total: {len(results)} | Success: {success_count} | Failed: {failed_count} | Warning: {warning_count}")
    
    # Save results
    os.makedirs("test-results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test-results/api_tests_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "test_suite": "API Connection Tests",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(results),
                "success": success_count,
                "failed": failed_count,
                "warning": warning_count
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    run_all_tests()
