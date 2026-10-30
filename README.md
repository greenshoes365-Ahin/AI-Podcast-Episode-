# AI Podcast Episode Production

Topic in → finished episode out.

```
topic ─► script (Claude) ─► voices (OpenAI / ElevenLabs TTS) ─► mix (pydub) ─► episode.mp3
                                   └──────────► transcript.txt + show_notes.md
```

## Setup
```bash
pip install -r requirements.txt     # also install ffmpeg (brew/apt install ffmpeg)
cp .env.example .env                # add your API keys
```
Optional: drop `intro.mp3` / `outro.mp3` into `assets/` for music.

## Usage
```bash
python main.py "How do vaccines train the immune system?" --minutes 10
python main.py "Quantum computing basics" --script-only      # review/edit the script first
python main.py --from-script episodes/<date>_<slug>/script.json   # then render audio
```
Output per episode in `episodes/<date>_<slug>/`: `script.json`, `episode.mp3`,
`transcript.txt` (timestamped), `show_notes.md`, and `segments/` (rendered lines;
re-runs reuse them, so a failed run resumes cheaply).

## Customising hosts
Pass `--hosts-file hosts.json` (same shape as `DEFAULT_HOSTS` in `podcast/config.py`):
name, persona, and a voice ID per provider. Any number of hosts works.

## Tests
`pytest`
