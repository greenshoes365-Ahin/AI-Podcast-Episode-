#!/usr/bin/env python3
"""CLI for AI podcast episode production.

Examples:
  python main.py "How do vaccines train the immune system?" --minutes 10
  python main.py "Quantum computing basics" --script-only
  python main.py --from-script episodes/2026-10-29_my-ep/script.json
"""
import argparse

from podcast.config import Settings, load_hosts
from podcast.pipeline import produce


def main():
    p = argparse.ArgumentParser(description="Produce an AI-generated podcast episode.")
    p.add_argument("topic", nargs="?", default="", help="Episode topic")
    p.add_argument("--minutes", type=int, default=8, help="Target length (default 8)")
    p.add_argument("--show", default="The AI Podcast", help="Show name")
    p.add_argument("--tone", default="smart but accessible")
    p.add_argument("--notes", default="", help="Extra notes or source text for the script")
    p.add_argument("--notes-file", help="Read extra notes/source material from a file")
    p.add_argument("--hosts-file", help="JSON file defining hosts and voices")
    p.add_argument("--tts", choices=["openai", "elevenlabs"], help="Override TTS_PROVIDER")
    p.add_argument("--script-only", action="store_true", help="Stop after writing script.json")
    p.add_argument("--from-script", help="Skip writing; produce audio from an edited script.json")
    p.add_argument("--no-notes", action="store_true", help="Skip show notes generation")
    a = p.parse_args()

    if not a.topic and not a.from_script:
        p.error("Provide a topic or --from-script.")

    settings = Settings()
    settings.hosts = load_hosts(a.hosts_file)
    if a.tts:
        settings.tts_provider = a.tts
    notes = a.notes
    if a.notes_file:
        notes += "\n" + open(a.notes_file, encoding="utf-8").read()

    produce(settings, a.topic, a.minutes, a.show, a.tone, notes,
            script_only=a.script_only, from_script=a.from_script, skip_notes=a.no_notes)


if __name__ == "__main__":
    main()
