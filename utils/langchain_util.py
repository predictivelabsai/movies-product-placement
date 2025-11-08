import os
from typing import Dict, Optional
from langchain_core.prompts import PromptTemplate
import json
import re

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None  # type: ignore


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name, "")
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")
    return value


def create_llm(selected_model: Dict[str, str], temperature: float = 0.5, max_tokens: int = 2000):
    """
    Create an LLM instance based on a selected_model dict:
    expected keys: {'provider': 'google'|'openai'|'xai', 'model': '<model-id>'}
    """
    provider = selected_model.get("provider")
    model = selected_model.get("model")

    if provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except Exception as e:
            raise RuntimeError("langchain_google_genai is not installed or failed to import") from e
        api_key = _require_env("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_tokens
        )

    if provider == "openai":
        if ChatOpenAI is None:
            raise RuntimeError("langchain_openai is not installed or failed to import")
        api_key = _require_env("OPENAI_API_KEY")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )

    if provider == "xai":
        if ChatOpenAI is None:
            raise RuntimeError("langchain_openai is not installed or failed to import")
        api_key = _require_env("XAI_API_KEY")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=temperature,
            max_tokens=max_tokens
        )

    raise ValueError(f"Unknown provider: {provider}")


def build_analysis_prompt(analysis_template: str, script_title: str, script_content: str) -> str:
    """Injects title and content into the standardized analysis template."""
    prompt_text = analysis_template.replace("{SCRIPT_TITLE}", script_title)
    prompt_text = f"""{prompt_text}

---

## SCREENPLAY EXCERPT TO ANALYZE:

{script_content[:15000]}

---

**IMPORTANT INSTRUCTIONS:**
- Follow the exact structure provided above
- Use markdown tables for all structured data
- Provide specific, actionable recommendations
- Include real brand names where appropriate
- Ensure all sections are comprehensive and detailed
- Focus on data consistency and professional formatting"""
    return prompt_text


def analyze_script(script_title: str, script_content: str, selected_model: Dict[str, str], temperature: float, max_tokens: int, analysis_template: str) -> str:
    """Creates the model, builds the prompt, and returns the analysis text."""
    llm = create_llm(selected_model, temperature=temperature, max_tokens=max_tokens)
    prompt_text = build_analysis_prompt(analysis_template, script_title, script_content)
    response = llm.invoke(prompt_text)
    return response.content if hasattr(response, "content") else str(response)


def build_comparison_prompt(template_text: str, original_script: str, modified_script: str) -> str:
    """Formats the comparison prompt with both scripts."""
    prompt = PromptTemplate(
        input_variables=["original_script", "modified_script"],
        template=template_text
    )
    return prompt.format(
        original_script=original_script,
        modified_script=modified_script
    )


def compare_scripts(original_script: str, modified_script: str, template_text: str, temperature: float = 0.5, model: str = "gpt-4.1-mini", provider: str = "openai", max_tokens: int = 1500) -> str:
    """
    Performs the AI comparison. Defaults to OpenAI but can be extended.
    """
    selected_model = {"provider": provider, "model": model}
    llm = create_llm(selected_model, temperature=temperature, max_tokens=max_tokens)
    formatted = build_comparison_prompt(template_text, original_script, modified_script)
    response = llm.invoke(formatted)
    return response.content if hasattr(response, "content") else str(response)

def _extract_json_block(text: str) -> str:
    """
    Extract a JSON block from a response that may include backticks or prose.
    """
    # Try to find code-fenced JSON
    fence = re.search(r"```json\\s*([\\s\\S]*?)\\s*```", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    # Fallback: find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text

def compare_scripts_json(original_script: str, modified_script: str, template_text: str, provider: str = "openai", model: str = "gpt-4.1-mini", temperature: float = 0.2, max_tokens: int = 1800) -> Dict:
    """
    Performs an AI comparison and expects STRICT JSON output describing changes.
    Returns a parsed Python dict. Raises if parsing fails.
    """
    selected_model = {"provider": provider, "model": model}
    llm = create_llm(selected_model, temperature=temperature, max_tokens=max_tokens)
    prompt = PromptTemplate(
        input_variables=["original_script", "modified_script"],
        template=template_text
    )
    formatted = prompt.format(
        original_script=original_script,
        modified_script=modified_script
    )
    response = llm.invoke(formatted)
    text = response.content if hasattr(response, "content") else str(response)
    json_str = _extract_json_block(text)
    try:
        return json.loads(json_str)
    except Exception:
        # Attempt a simple cleanup (remove trailing prose)
        try:
            cleaned = json_str.strip()
            # If model returned bare key-value pairs without outer braces, wrap them
            if cleaned and not cleaned.lstrip().startswith("{") and '"summary"' in cleaned:
                cleaned = "{\n" + cleaned + "\n}"
            # Ensure we end at the last closing brace
            if "}" in cleaned and cleaned.count("{") != cleaned.count("}"):
                # Trim after the last closing brace
                cleaned = cleaned[: cleaned.rfind("}") + 1]
            return json.loads(cleaned)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON from model output: {e}")

def generate_modified_script(original_script: str, template_text: str, provider: str = "openai", model: str = "gpt-4.1-mini", temperature: float = 0.4, max_tokens: int = 3500) -> str:
    """
    Generates a modified version of the script with product placements,
    preserving story and character arcs.
    """
    selected_model = {"provider": provider, "model": model}
    llm = create_llm(selected_model, temperature=temperature, max_tokens=max_tokens)
    prompt = PromptTemplate(
        input_variables=["original_script"],
        template=template_text
    )
    formatted = prompt.format(original_script=original_script)
    response = llm.invoke(formatted)
    return response.content if hasattr(response, "content") else str(response)


