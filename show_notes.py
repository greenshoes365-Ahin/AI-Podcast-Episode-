"""Transcript, chapters, and show notes."""
from .llm import ask, parse_json

SYSTEM = "You write concise podcast marketing copy. Reply with ONLY valid JSON."

PROMPT = """From this podcast transcript, produce JSON:
{{
  "description": "2-3 sentence episode description for podcast apps",
  "key_takeaways": ["3-5 short bullets"],
  "keywords": ["5-8 SEO keywords"],
  "social_post": "One engaging post (under 280 characters, no hashtags spam)"
}}

Title: {title}

Transcript:
{transcript}"""


def build_transcript(script, starts=None) -> str:
    lines = []
    for i, s in enumerate(script["segments"]):
        stamp = f"[{fmt_time(starts[i])}] " if starts else ""
        lines.append(f"{stamp}{s['speaker']}: {s['text']}")
    return "\n\n".join(lines)


def chapters(script, starts):
    """First timestamp of each distinct `section`."""
    seen, out = set(), []
    for s, t in zip(script["segments"], starts):
        sec = s.get("section")
        if sec and sec not in seen:
            seen.add(sec)
            out.append((t, sec))
    return out


def fmt_time(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def generate_show_notes(settings, script, starts) -> str:
    transcript = build_transcript(script)
    meta = parse_json(ask(settings.claude_model, SYSTEM,
                          PROMPT.format(title=script["title"], transcript=transcript),
                          max_tokens=2000))
    md = [f"# {script['title']}", "", meta["description"], "", "## Key takeaways"]
    md += [f"- {t}" for t in meta["key_takeaways"]]
    md += ["", "## Chapters"]
    md += [f"- {fmt_time(t)} — {name}" for t, name in chapters(script, starts)]
    md += ["", "## Keywords", ", ".join(meta["keywords"]),
           "", "## Social post", meta["social_post"]]
    return "\n".join(md) + "\n"
