#!/bin/bash
# Evening reflection prompt - runs at 9 PM daily

DATE=$(date +%Y-%m-%d)
MESSAGE="Evening reflection time, Matthew.

1. What did you learn today?
2. What are you grateful for?
3. One thing you want to do differently tomorrow?

Reply here and I'll save your answers to the journal."

# Send message via OpenClaw message tool
openclaw message send --channel telegram --target 5162768065 --message "$MESSAGE"
