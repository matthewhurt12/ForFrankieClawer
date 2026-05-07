# voice-output

Use this skill when Matthew asks for a voice file, audio version, TTS,
ElevenLabs, `sag`, narration, storytime, or says "read it to me."

This skill is for navigation and safe handling. Do not assume the TTS helper is
installed in the current shell. Check first.

## First Checks

```powershell
Get-Command sag -ErrorAction SilentlyContinue
sag --help
```

If `sag` is not found, say that the local ElevenLabs helper is not on PATH and
offer a text draft that can be voiced later. Do not fake an audio file.

## Output Location

Save generated voice files under:

```text
data/voice_outputs/
```

Use descriptive filenames:

```text
data/voice_outputs/athens_food_pick_YYYY-MM-DD.mp3
data/voice_outputs/storytime_YYYY-MM-DD.mp3
```

Generated audio files are local output and should not be committed unless
Matthew explicitly asks.

## What To Voice

Good voice uses:

- restaurant picks
- storytime / movie summaries
- short explanations Matthew wants to hear instead of read
- playful summaries

Keep scripts conversational. For restaurant picks, lead with the actual pick,
then give 2-3 backup options.

## Safety

- Never print ElevenLabs keys.
- Never commit `.env`, tokens, or generated voice output.
- If the voice command requires a token and it is missing, ask Matthew to set it
  in the environment.
- If the request involves sending audio to someone else, ask before sending.
