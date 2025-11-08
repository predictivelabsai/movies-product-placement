import json
import os
from datetime import datetime
from dotenv import load_dotenv

from utils.langchain_util import compare_scripts, analyze_script

# Load environment variables from .env at project root
load_dotenv()


def ensure_dirs():
    os.makedirs("test-results", exist_ok=True)
    os.makedirs("prompts", exist_ok=True)


def test_compare_scripts():
    original = "INT. CAFE - DAY\nAlice sips coffee while reading a book."
    modified = "INT. CAFE - DAY\nAlice sips a Starbucks coffee while reading a book. The cup logo faces camera."

    # Minimal template to drive structure
    template = (
        "Compare ORIGINAL and MODIFIED focusing only on product placements and cinematography.\n"
        "## New Product Placements (Clever Integrations)\n"
        "{original_script}\n---\n{modified_script}\n"
    )

    if not os.getenv("OPENAI_API_KEY"):
        return {
            "name": "compare_scripts (openai)",
            "skipped": True,
            "reason": "OPENAI_API_KEY missing"
        }

    try:
        result = compare_scripts(
            original_script=original,
            modified_script=modified,
            template_text=template,
            temperature=0.2,
            model="gpt-4.1-mini",
            provider="openai",
            max_tokens=600
        )
        return {
            "name": "compare_scripts (openai)",
            "skipped": False,
            "ok": isinstance(result, str) and len(result) > 0
        }
    except Exception as e:
        return {
            "name": "compare_scripts (openai)",
            "skipped": False,
            "ok": False,
            "error": str(e)
        }


def test_analyze_script():
    if not (os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("XAI_API_KEY")):
        return {
            "name": "analyze_script (any provider)",
            "skipped": True,
            "reason": "No API keys present"
        }

    # Prefer OpenAI if available
    if os.getenv("OPENAI_API_KEY"):
        selected_model = {"provider": "openai", "model": "gpt-4.1-mini"}
    elif os.getenv("GOOGLE_API_KEY"):
        selected_model = {"provider": "google", "model": "gemini-2.0-flash-exp"}
    else:
        selected_model = {"provider": "xai", "model": "grok-3"}

    analysis_template = "## EXPERT SCREENPLAY ANALYSIS: {SCRIPT_TITLE}\n\nProvide 1-2 bullet points.\n"
    script_title = "Test Script"
    script_content = "EXT. PARK - DAY\nA runner passes a bench."

    try:
        result = analyze_script(
            script_title=script_title,
            script_content=script_content,
            selected_model=selected_model,
            temperature=0.1,
            max_tokens=400,
            analysis_template=analysis_template
        )
        return {
            "name": f"analyze_script ({selected_model['provider']})",
            "skipped": False,
            "ok": isinstance(result, str) and len(result) > 0
        }
    except Exception as e:
        return {
            "name": f"analyze_script ({selected_model['provider']})",
            "skipped": False,
            "ok": False,
            "error": str(e)
        }


def main():
    ensure_dirs()
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": {"passed": 0, "failed": 0, "skipped": 0},
        "checks": []
    }

    for fn in [test_compare_scripts, test_analyze_script]:
        out = fn()
        results["checks"].append(out)

    for c in results["checks"]:
        if c.get("skipped"):
            results["summary"]["skipped"] += 1
        elif c.get("ok"):
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join("test-results", f"ai_smoke_{ts}.json")
    txt_path = os.path.join("test-results", f"ai_smoke_{ts}.txt")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    lines = [
        f"AI SMOKE TEST RESULTS @ {results['timestamp']}",
        f"Passed: {results['summary']['passed']}  Failed: {results['summary']['failed']}  Skipped: {results['summary']['skipped']}",
        "-" * 60,
    ]
    for c in results["checks"]:
        status = "SKIP" if c.get("skipped") else ("PASS" if c.get("ok") else "FAIL")
        name = c.get("name", "unknown")
        suffix = f" ({c.get('reason')})" if c.get("skipped") and c.get("reason") else (f" - {c.get('error')}" if c.get("error") else "")
        lines.append(f"[{status}] {name}{suffix}")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {txt_path}")


if __name__ == "__main__":
    main()


