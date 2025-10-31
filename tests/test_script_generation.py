"""
Test script generation functionality
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_prompt_template_loading():
    """Test loading prompt template"""
    print("Testing prompt template loading...")
    
    try:
        prompt_file = "prompts/script_generation.txt"
        
        if not os.path.exists(prompt_file):
            return {
                "test": "Prompt Template Loading",
                "status": "FAILED",
                "error": "Prompt file not found",
                "timestamp": datetime.now().isoformat()
            }
        
        with open(prompt_file, 'r') as f:
            content = f.read()
        
        # Check for required placeholders
        required_placeholders = ['{genre}', '{target_audience}', '{setting}']
        missing_placeholders = [p for p in required_placeholders if p not in content]
        
        if missing_placeholders:
            return {
                "test": "Prompt Template Loading",
                "status": "WARNING",
                "message": f"Missing placeholders: {', '.join(missing_placeholders)}",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "test": "Prompt Template Loading",
            "status": "SUCCESS",
            "template_length": len(content),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test": "Prompt Template Loading",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_script_generation():
    """Test AI script generation"""
    print("Testing AI script generation...")
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "test": "Script Generation",
                "status": "FAILED",
                "error": "OpenAI API key not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        # Load prompt template
        with open("prompts/script_generation.txt", 'r') as f:
            template = f.read()
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7, max_tokens=500)
        
        # Create prompt
        prompt_template = PromptTemplate(
            input_variables=["genre", "target_audience", "setting"],
            template=template
        )
        
        # Format and generate script
        formatted_prompt = prompt_template.format(
            genre="Thriller",
            target_audience="General Audience (PG-13)",
            setting="Modern urban city"
        )
        
        response = llm.invoke(formatted_prompt)
        result = response.content
        
        # Save test script
        os.makedirs("scripts", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scripts/test_{timestamp}_Thriller.txt"
        
        with open(filename, 'w') as f:
            f.write(f"TEST SCRIPT\n")
            f.write(f"Genre: Thriller\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*80 + "\n\n")
            f.write(result)
        
        return {
            "test": "Script Generation",
            "status": "SUCCESS",
            "script_length": len(result),
            "output_file": filename,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test": "Script Generation",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_script_storage():
    """Test script storage functionality"""
    print("Testing script storage...")
    
    try:
        scripts_dir = "scripts"
        
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        
        # Check if directory is writable
        test_file = os.path.join(scripts_dir, "test_write.txt")
        
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Verify file was created
        if os.path.exists(test_file):
            os.remove(test_file)
            
            return {
                "test": "Script Storage",
                "status": "SUCCESS",
                "scripts_directory": scripts_dir,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "test": "Script Storage",
                "status": "FAILED",
                "error": "Could not verify file creation",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {
            "test": "Script Storage",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        import sqlite3
        
        db_file = "vadis_media.db"
        
        if not os.path.exists(db_file):
            return {
                "test": "Database Connection",
                "status": "WARNING",
                "message": "Database file not found",
                "timestamp": datetime.now().isoformat()
            }
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        conn.close()
        
        expected_tables = ['scripts', 'product_placements', 'actors', 'script_casting', 'revenue_forecasts']
        found_tables = [t[0] for t in tables]
        missing_tables = [t for t in expected_tables if t not in found_tables]
        
        if missing_tables:
            return {
                "test": "Database Connection",
                "status": "WARNING",
                "message": f"Missing tables: {', '.join(missing_tables)}",
                "found_tables": found_tables,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "test": "Database Connection",
            "status": "SUCCESS",
            "tables_count": len(tables),
            "tables": found_tables,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test": "Database Connection",
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_all_tests():
    """Run all script generation tests"""
    print("="*80)
    print("Vadis Media Product Placement - Script Generation Tests")
    print("="*80)
    print()
    
    results = []
    
    # Run tests
    results.append(test_prompt_template_loading())
    results.append(test_script_storage())
    results.append(test_database_connection())
    results.append(test_script_generation())
    
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
        print(f"{status_symbol} {result['test']}: {result['status']}")
    
    print()
    print(f"Total: {len(results)} | Success: {success_count} | Failed: {failed_count} | Warning: {warning_count}")
    
    # Save results
    os.makedirs("test-results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test-results/script_generation_tests_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "test_suite": "Script Generation Tests",
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
