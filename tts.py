"""Text-to-speech providers behind one interface."""
import os
from abc import ABC, abstractmethod
from pathlib import Path

import requests


class TTSProvider(ABC):
    name: str

    @abstractmethod
    def synthesize(self, text: str, voice: str, out_path: Path) -> Path:
        """Render `text` with `voice` into an mp3 at `out_path`."""


class OpenAITTS(TTSProvider):
    name = "openai"

    def __init__(self, model: str):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def synthesize(self, text, voice, out_path):
        with self.client.audio.speech.with_streaming_response.create(
            model=self.model, voice=voice, input=text, response_format="mp3"
        ) as resp:
            resp.stream_to_file(out_path)
        return out_path


class ElevenLabsTTS(TTSProvider):
    name = "elevenlabs"

    def __init__(self, model: str):
        self.key = os.environ["ELEVENLABS_API_KEY"]
        self.model = model

    def synthesize(self, text, voice, out_path):
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
            headers={"xi-api-key": self.key, "accept": "audio/mpeg"},
            json={"text": text, "model_id": self.model},
            timeout=120,
        )
        r.raise_for_status()
        Path(out_path).write_bytes(r.content)
        return out_path


def get_provider(settings) -> TTSProvider:
    if settings.tts_provider == "openai":
        return OpenAITTS(settings.openai_tts_model)
    if settings.tts_provider == "elevenlabs":
        return ElevenLabsTTS(settings.elevenlabs_model)
    raise ValueError(f"Unknown TTS provider: {settings.tts_provider}")
