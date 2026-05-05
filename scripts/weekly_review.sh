#!/bin/bash
# Weekly memory review - runs every Sunday at 7 PM

WORKSPACE="/home/matthew/openclaw-vault"
WEEK_START=$(date -d "7 days ago" +%Y-%m-%d)
WEEK_END=$(date +%Y-%m-%d)

MESSAGE="Weekly review time.

I'm reading daily files from $WEEK_START to $WEEK_END to pull insights into MEMORY.md and project journals.

I'll send you a summary of what I noticed in a moment."

# Send message via OpenClaw
openclaw message send --channel telegram --target 5162768065 --message "$MESSAGE"

# Trigger the actual review via a follow-up session message
# The agent will handle the heavy lifting of reading files and updating memory
openclaw message send --channel telegram --target 5162768065 --message "[INTERNAL] Run weekly review: analyze memory files from $WEEK_START to $WEEK_END, update MEMORY.md and project journals with notable patterns/decisions/concerns, then send Matthew a summary."
