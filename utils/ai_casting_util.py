import os
import re
import requests
from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate
from utils.langchain_util import create_llm
from tmdbv3api import TMDb, Person
from tavily import TavilyClient
from langgraph.graph import StateGraph, START, END


def _load_casting_template() -> str:
    # Prefer markdown prompt, fallback to .py if provided
    md_path = "prompts/ai_casting_matching_template.md"
    py_path = "prompts/ai_casting_matching_template.py"
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()
    if os.path.exists(py_path):
        with open(py_path, "r", encoding="utf-8") as f:
            return f.read()
    # Minimal fallback
    return (
        "You are a senior casting director. Based on the SCRIPT, recommend 5 actors.\n"
        "For each actor include: Name; Target role in THIS script; Why they fit; 2-3 similar roles; Draw.\n"
        "SCRIPT:\n{script_text}\n"
    )


def _tmdb_search_person(name: str) -> Dict[str, Any]:
    try:
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key:
            return {}
        tmdb = TMDb()
        tmdb.api_key = api_key
        tmdb.language = "en"
        person_api = Person()
        results = person_api.search(name)
        if not results:
            return {}
        p = results[0]
        # Additional details could be fetched if needed
        return {"id": p.id, "name": p.name, "popularity": getattr(p, "popularity", None)}
    except Exception:
        return {}


def _tmdb_person_roles(person_id: int, max_roles: int = 3) -> List[Dict[str, Any]]:
    try:
        api_key = os.getenv("TMDB_API_KEY")
        if not api_key or not person_id:
            return []
        person_api = Person()
        credits = person_api.movie_credits(person_id)
        cast = credits.get("cast", []) if isinstance(credits, dict) else getattr(credits, "cast", [])
        # Sort by popularity/vote_count descending
        cast_sorted = sorted(cast, key=lambda c: (c.get("vote_count", 0) or 0, c.get("popularity", 0) or 0), reverse=True)
        roles = []
        for c in cast_sorted[:max_roles]:
            roles.append({
                "title": c.get("title") or c.get("original_title"),
                "year": (c.get("release_date") or "")[:4],
                "character": c.get("character")
            })
        return roles
    except Exception:
        return []


def _omdb_lookup_title(title: str, year: str = "") -> Dict[str, Any]:
    try:
        key = os.getenv("OMDB_API_KEY")
        if not key or not title:
            return {}
        params = {"apikey": key, "t": title}
        if year and year.isdigit():
            params["y"] = year
        r = requests.get("http://www.omdbapi.com/", params=params, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {}
    except Exception:
        return {}


def _tavily_search_roles(actor_name: str, max_results: int = 3) -> List[Dict[str, str]]:
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return []
        client = TavilyClient(api_key=api_key)
        q = f"best roles of {actor_name} filmography notable performances"
        res = client.search(q, include_answer=False)
        out = []
        for item in res.get("results", [])[:max_results]:
            out.append({"title": item.get("title", ""), "url": item.get("url", "")})
        return out
    except Exception:
        return []


def generate_recommendations(
    script_text: str,
    selected_model: Dict[str, str],
    temperature: float = 0.4,
    max_tokens: int = 1200,
    enabled_tools: Optional[Dict[str, bool]] = None
) -> str:
    """
    Uses a simple LangGraph pipeline:
    1) propose: LLM proposes candidates + target roles (JSON)
    2) augment: fetch similar roles from TMDb/OMDb/Tavily
    3) compose: LLM composes final markdown with Target Role and Similar Roles
    """
    template = _load_casting_template()
    llm = create_llm(selected_model, temperature=temperature, max_tokens=max_tokens)

    def propose_node(state: Dict[str, Any]) -> Dict[str, Any]:
        sys_prompt = (
            "Return STRICT JSON with field 'candidates': "
            "[{ 'name': 'Actor', 'target_role': 'short role desc in this script' }, ...]. "
            "Do not include prose."
        )
        prompt = f"{sys_prompt}\n\nSCRIPT:\n{state['script_text'][:8000]}"
        resp = llm.invoke(prompt)
        text = resp.content if hasattr(resp, "content") else str(resp)
        # Extract JSON
        import json as _json
        try:
            start = text.find("{")
            end = text.rfind("}")
            obj = _json.loads(text[start:end+1])
            return {"candidates": obj.get("candidates", [])}
        except Exception:
            # fallback: single candidate list empty
            return {"candidates": []}

    def augment_node(state: Dict[str, Any]) -> Dict[str, Any]:
        enriched = []
        flags = state.get("enabled_tools") or {}
        use_tmdb = bool(flags.get("tmdb", True))
        use_omdb = bool(flags.get("omdb", True))
        use_tavily = bool(flags.get("tavily", True))
        for c in state.get("candidates", [])[:5]:
            name = c.get("name", "")
            tmdb_p = _tmdb_search_person(name) if use_tmdb else {}
            roles = _tmdb_person_roles(tmdb_p.get("id")) if (use_tmdb and tmdb_p) else []
            # Optionally enrich via OMDb for first role
            omdb = _omdb_lookup_title(roles[0]["title"], roles[0]["year"]) if (use_omdb and roles) else {}
            tav = _tavily_search_roles(name) if use_tavily else []
            enriched.append({
                "name": name,
                "target_role": c.get("target_role", ""),
                "tmdb_roles": roles,
                "omdb_first": {"Title": omdb.get("Title"), "Year": omdb.get("Year"), "imdbRating": omdb.get("imdbRating")},
                "tavily": tav
            })
        return {"enriched": enriched}

    def compose_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Ask LLM to compose final markdown separating Target Role and Similar Roles
        from langchain_core.prompts import PromptTemplate as _PT
        comp_template = _PT(
            input_variables=["script_text", "enriched"],
            template=(
                "SCRIPT:\n{script_text}\n\n"
                "CANDIDATES WITH EVIDENCE:\n{enriched}\n\n"
                "Compose a production-ready list of 5 actors. For each entry use:\n"
                "- Name\n"
                "- Target role: (from the script)\n"
                "- Why: (2–3 sentences grounded in the script)\n"
                "- Similar roles: bullet list of 2–3 roles (Title – Year) using the evidence\n"
                "- Estimated draw: low | medium | high + short rationale\n"
                "Ensure actors are age-appropriate versus the implied era/timeline in the script. "
                "If mismatch is detected, exclude or flag and replace with a better fit.\n"
            )
        )
        formatted = comp_template.format(
            script_text=state.get("script_text", "")[:8000],
            enriched=str(state.get("enriched", ""))[:8000]
        )
        resp = llm.invoke(formatted)
        text = resp.content if hasattr(resp, "content") else str(resp)
        return {"markdown": text}

    # Build and run graph
    graph = StateGraph(dict)
    graph.add_node("propose", propose_node)
    graph.add_node("augment", augment_node)
    graph.add_node("compose", compose_node)
    graph.add_edge(START, "propose")
    graph.add_edge("propose", "augment")
    graph.add_edge("augment", "compose")
    graph.add_edge("compose", END)
    app = graph.compile()
    result = app.invoke({"script_text": script_text, "enabled_tools": enabled_tools or {}})
    return result.get("markdown", "No recommendations generated.")


def score_actor_for_script(actor_name: str, script_text: str, selected_model: Dict[str, str], temperature: float = 0.2, max_tokens: int = 600) -> Dict[str, Any]:
    llm = create_llm(selected_model, temperature=temperature, max_tokens=max_tokens)
    template = (
        "You are evaluating casting suitability for the SCRIPT.\n"
        "Actor: {actor_name}\n\n"
        "SCRIPT:\n{script_text}\n\n"
        "Task:\n"
        "- Provide a 3-5 bullet justification referencing the script's roles, tone, and era/age consistency\n"
        "- Output a final line: 'Score: NN/100' (integer 0-100)\n"
    )
    prompt = PromptTemplate(
        input_variables=["actor_name", "script_text"],
        template=template
    )
    formatted = prompt.format(actor_name=actor_name, script_text=script_text[:20000])
    resp = llm.invoke(formatted)
    text = resp.content if hasattr(resp, "content") else str(resp)
    m = re.search(r"Score:\s*(\d{1,3})\s*/\s*100", text)
    score = None
    if m:
        try:
            score = int(m.group(1))
        except Exception:
            score = None
    return {"analysis": text, "score": score}


