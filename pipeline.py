"""Orchestrates the full episode production flow."""
import json
import re
from datetime import date
from pathlib import Path

from . import audio, scriptwriter, show_notes, tts


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "episode"


def produce(settings, topic, minutes=8, show="The AI Podcast", tone="smart but accessible",
            notes="", script_only=False, from_script=None, skip_notes=False) -> Path:
    if from_script:
        script = json.loads(Path(from_script).read_text(encoding="utf-8"))
        scriptwriter.validate_script(script, [h["name"] for h in settings.hosts])
        print(f"Loaded script: {script['title']}")
    else:
        print("1/4 Writing script...")
        script = scriptwriter.generate_script(settings, topic, minutes, show, tone, notes)

    ep_dir = settings.output_root / f"{date.today():%Y-%m-%d}_{slugify(script['title'])}"
    seg_dir = ep_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"    Title: {script['title']}  ({len(script['segments'])} segments)")
    if script_only:
        print(f"Script saved to {ep_dir / 'script.json'}")
        return ep_dir

    print("2/4 Generating voices...")
    provider = tts.get_provider(settings)
    voices = {h["name"]: h["voices"][settings.tts_provider] for h in settings.hosts}
    files = []
    for i, seg in enumerate(script["segments"]):
        path = seg_dir / f"{i:04d}_{seg['speaker']}.mp3"
        if not path.exists():  # resume support: skip already-rendered lines
            provider.synthesize(seg["text"], voices[seg["speaker"]], path)
        files.append(path)
        print(f"    {i + 1}/{len(script['segments'])}", end="\r")
    print()

    print("3/4 Mixing episode...")
    starts = audio.assemble(files, settings, ep_dir / "episode.mp3")
    (ep_dir / "transcript.txt").write_text(show_notes.build_transcript(script, starts), encoding="utf-8")

    if not skip_notes:
        print("4/4 Writing show notes...")
        (ep_dir / "show_notes.md").write_text(
            show_notes.generate_show_notes(settings, script, starts), encoding="utf-8")

    print(f"Done! Episode ready in {ep_dir}")
    return ep_dir
