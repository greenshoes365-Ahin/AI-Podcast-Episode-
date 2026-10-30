"""Turn a topic into a multi-host podcast script."""
from .llm import ask, parse_json

SYSTEM = """You are a podcast scriptwriter. Write natural, engaging conversational
dialogue for spoken audio: short sentences, contractions, occasional reactions,
no stage directions, no markdown, no emojis, no sound-effect cues.
Reply with ONLY valid JSON, no commentary."""

PROMPT = """Write a script for one podcast episode.

Show: {show}
Topic: {topic}
Target length: about {minutes} minutes (~{words} words of dialogue)
Audience / tone: {tone}

Hosts:
{hosts}

Extra notes / source material:
{notes}

Structure: a hook, a quick intro of the topic, 3-4 substantive sections,
a recap of key takeaways, and a short sign-off. Only use facts you are
confident about; if unsure, keep claims general.

Return JSON in exactly this shape:
{{
  "title": "Episode title",
  "summary": "One-paragraph episode description",
  "segments": [
    {{"speaker": "<host name exactly as given>", "text": "spoken line(s)", "section": "Section name"}}
  ]
}}"""


def generate_script(settings, topic, minutes=8, show="The AI Podcast",
                    tone="smart but accessible", notes="") -> dict:
    hosts = "\n".join(f"- {h['name']}: {h['persona']}" for h in settings.hosts)
    prompt = PROMPT.format(
        show=show, topic=topic, minutes=minutes, words=int(minutes * 150),
        tone=tone, hosts=hosts, notes=notes or "(none)",
    )
    script = parse_json(ask(settings.claude_model, SYSTEM, prompt, max_tokens=12000))
    validate_script(script, [h["name"] for h in settings.hosts])
    return script


def validate_script(script: dict, host_names: list) -> None:
    segs = script.get("segments")
    if not segs:
        raise ValueError("Script has no segments.")
    for i, s in enumerate(segs):
        if s.get("speaker") not in host_names:
            raise ValueError(f"Segment {i}: unknown speaker {s.get('speaker')!r}")
        if not str(s.get("text", "")).strip():
            raise ValueError(f"Segment {i}: empty text")
