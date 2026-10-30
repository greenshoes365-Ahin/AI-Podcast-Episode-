"""Thin wrapper around the Anthropic API plus robust JSON parsing."""
import json
import re

from anthropic import Anthropic

_client = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()  # reads ANTHROPIC_API_KEY
    return _client


def ask(model: str, system: str, prompt: str, max_tokens: int = 8000) -> str:
    resp = client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def parse_json(text: str) -> dict:
    """Parse JSON from a model reply, tolerating ```json fences and stray prose."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise
