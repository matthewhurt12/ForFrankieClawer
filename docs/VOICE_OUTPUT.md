# Voice Output / ElevenLabs

Frankie can use local voice tooling when Matthew asks for a voice file or audio
version.

Primary skill:

```text
skills/voice-output/SKILL.md
```

## Check Availability

```powershell
Get-Command sag -ErrorAction SilentlyContinue
sag --help
```

If `sag` is not available, Frankie should say so plainly and prepare a voice
script instead of pretending an audio file was generated.

## Save Outputs

```text
data/voice_outputs/
```

That folder is ignored by git.
