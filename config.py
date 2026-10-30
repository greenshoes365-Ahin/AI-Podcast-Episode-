"""Configuration: environment settings and host (voice) definitions."""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Each host has a persona (fed to the scriptwriter) and a voice per TTS provider.
DEFAULT_HOSTS = [
    {
        "name": "Alex",
        "persona": "Curious, upbeat lead host who asks the questions listeners would ask.",
        "voices": {"openai": "alloy", "elevenlabs": "21m00Tcm4TlvDq8ikWAM"},
    },
    {
        "name": "Sam",
        "persona": "Calm, knowledgeable co-host who explains with analogies and dry humor.",
        "voices": {"openai": "onyx", "elevenlabs": "pNInz6obpgDQGcFmaJgB"},
    },
]


@dataclass
class Settings:
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
    tts_provider: str = os.getenv("TTS_PROVIDER", "openai").lower()
    openai_tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    elevenlabs_model: str = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
    pause_ms: int = 350            # silence between speaker turns
    target_dbfs: float = -16.0     # loudness target for the final mix
    music_gain_db: float = -18.0   # intro/outro music level relative to speech
    output_root: Path = Path("episodes")
    assets_dir: Path = Path("assets")  # intro.mp3 / outro.mp3 are used if present
    hosts: list = field(default_factory=lambda: list(DEFAULT_HOSTS))


def load_hosts(path: str | None) -> list:
    """Load custom hosts from a JSON file (same shape as DEFAULT_HOSTS)."""
    if not path:
        return list(DEFAULT_HOSTS)
    return json.loads(Path(path).read_text(encoding="utf-8"))
