
import os
import json
from typing import List, Dict, Any, Optional

import openai


def call_openai_chat(model: str, messages: List[Dict[str, str]], temperature: float = 0.5) -> str:
    """
    Thin wrapper around OpenAI ChatCompletion.create using the fixed model (gpt-3.5-turbo).
    Requires OPENAI_API_KEY in the environment. No streaming to keep code simple and testable.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Light sanity: the brief requires OpenAI's model; avoid using a Gemini key by mistake.
    if api_key.startswith("AI") or api_key.startswith("AIza"):
        raise RuntimeError("Detected a Google/Gemini API key in OPENAI_API_KEY. Use a valid OpenAI key (sk-...).")

    openai.api_key = api_key
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        stream=False,
        temperature=temperature,
        max_tokens=1600,  # slightly higher to comfortably fit 350-550 words + JSON when needed
    )
    return resp.choices[0].message["content"]  


def word_count(text: str) -> int:
    return len(text.strip().split())


def try_parse_json(s: str) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(s)
        # Light contract check
        if not isinstance(data, dict):
            return None
        if "scores" not in data or "overall" not in data or "actionable_feedback" not in data:
            return None
        return data
    except Exception:
        return None
