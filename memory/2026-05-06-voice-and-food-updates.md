# 2026-05-06 - Voice Navigation and Food Exclusions

Matthew wanted Frankie to find ElevenLabs / voice-file output easily when asked
for audio, and wanted Athens food recommendations to support excluding cuisines,
areas, speeds, tags, or text.

Added:

- `skills/voice-output/SKILL.md`
- `docs/VOICE_OUTPUT.md`
- `data/voice_outputs/` as ignored output location

Updated Athens food:

- `--exclude-cuisine`
- `--exclude-area`
- `--exclude-speed`
- `--exclude-tag`
- `--exclude`

Example:

```powershell
python scripts\athens_food.py recommend --mood "cheap quick" --exclude-cuisine brewery
python scripts\athens_food.py random --exclude-cuisine breakfast --exclude-area dt
```
