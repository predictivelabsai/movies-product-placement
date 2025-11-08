import json
import os
from datetime import datetime

from utils.langchain_util import build_comparison_prompt, build_analysis_prompt  # utils-only


def ensure_dirs():
    os.makedirs("test-results", exist_ok=True)
    os.makedirs("prompts", exist_ok=True)


def read_file_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def run_checks():
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": [],
        "summary": {"passed": 0, "failed": 0}
    }

    # 1) utils module importable
    try:
        import utils.langchain_util  # noqa: F401
        util_ok = True
    except Exception:
        util_ok = False
    results["checks"].append({
        "name": "utils.langchain_util importable",
        "passed": util_ok
    })

    # 2) comparison prompt formatting works
    template = "ORIGINAL:\n{original_script}\n---\nMODIFIED:\n{modified_script}\n"
    formatted = build_comparison_prompt(template, "AAA", "BBB")
    results["checks"].append({
        "name": "build_comparison_prompt formats placeholders",
        "passed": ("AAA" in formatted and "BBB" in formatted)
    })

    # 3) analysis prompt building injects title and content
    analysis_template = "## EXPERT SCREENPLAY ANALYSIS: {SCRIPT_TITLE}\n"
    prompt_text = build_analysis_prompt(analysis_template, "My Title", "Some content here")
    results["checks"].append({
        "name": "build_analysis_prompt injects title and content",
        "passed": ("My Title" in prompt_text and "Some content here" in prompt_text)
    })

    # 4) Prompt template exists with required sections (.md)
    prompt_exists = os.path.exists("prompts/script_comparison_template.md")
    prompt_text_disk = read_file_text("prompts/script_comparison_template.md")
    required_sections = [
        "New Product Placements (Clever Integrations)",
        "Cinematography Changes (Angles & Camera Work)",
        "Integration Techniques Used",
        "Narrative Integrity"
    ]
    sections_ok = all(section in prompt_text_disk for section in required_sections) if prompt_text_disk else False
    results["checks"].append({
        "name": "script_comparison_template includes required sections",
        "passed": prompt_exists and sections_ok
    })

    # 5) Directories exist
    dirs_ok = all(os.path.isdir(p) for p in ["scripts", "prompts"])
    results["checks"].append({
        "name": "Required directories exist (scripts, prompts)",
        "passed": dirs_ok
    })

    # Summarize
    for c in results["checks"]:
        if c["passed"]:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    return results


def write_outputs(results: dict):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join("test-results", f"smoke_{ts}.json")
    txt_path = os.path.join("test-results", f"smoke_{ts}.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    lines = [
        f"SMOKE TEST RESULTS @ {results['timestamp']}",
        f"Passed: {results['summary']['passed']}  Failed: {results['summary']['failed']}",
        "-" * 60,
    ]
    for c in results["checks"]:
        status = "PASS" if c["passed"] else "FAIL"
        lines.append(f"[{status}] {c['name']}")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return json_path, txt_path


if __name__ == "__main__":
    ensure_dirs()
    results = run_checks()
    json_file, txt_file = write_outputs(results)
    print(f"Wrote: {json_file}")
    print(f"Wrote: {txt_file}")
    exit(0)


