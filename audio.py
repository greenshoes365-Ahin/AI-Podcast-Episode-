"""Assemble speech segments into a finished, normalized episode (needs ffmpeg)."""
from pathlib import Path

from pydub import AudioSegment, effects


def assemble(segment_files, settings, out_path: Path):
    """Concatenate segments with pauses, add optional intro/outro, normalize, export.

    Returns a list of start times (seconds) for each segment, measured in the
    final episode, so chapters/transcripts line up with the audio.
    """
    pause = AudioSegment.silent(duration=settings.pause_ms)
    speech = AudioSegment.empty()
    starts = []
    for f in segment_files:
        starts.append(len(speech) / 1000)
        speech += AudioSegment.from_file(f) + pause
    speech = effects.normalize(speech)
    speech = speech.apply_gain(settings.target_dbfs - speech.dBFS)

    intro = _load_music(settings.assets_dir / "intro.mp3", settings)
    outro = _load_music(settings.assets_dir / "outro.mp3", settings)
    offset = len(intro) / 1000 if intro else 0.0
    episode = (intro or AudioSegment.empty()) + speech + (outro or AudioSegment.empty())

    episode.export(out_path, format="mp3", bitrate="128k", tags={"genre": "Podcast"})
    return [round(s + offset, 2) for s in starts]


def _load_music(path: Path, settings):
    if not path.exists():
        return None
    clip = AudioSegment.from_file(path)
    clip = clip.apply_gain(settings.target_dbfs + settings.music_gain_db - clip.dBFS)
    return clip.fade_in(300).fade_out(1500)
