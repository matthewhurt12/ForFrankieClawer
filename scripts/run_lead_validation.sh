#!/bin/bash
# LEAD_VALIDATION_RUN_001
# Scans 12 target models for active market context

set -e

MODELS=(
  "McIntosh MA 5100"
  "McIntosh MA 6100"
  "McIntosh C22"
  "Pioneer SX-1250"
  "Pioneer SX-1050"
  "Marantz 2270"
  "Marantz 2275"
  "Sansui G-9000"
  "Technics SL-1200"
  "Nakamichi Dragon"
  "Nakamichi 1000ZXL"
  "JBL L100"
)

OUTPUT_DIR="data/lead_validation_001"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "LEAD_VALIDATION_RUN_001"
echo "========================================"
echo "Scanning ${#MODELS[@]} target models..."
echo ""

for MODEL in "${MODELS[@]}"; do
  echo "Searching: $MODEL"
  python3 ebay_active_context.py "$MODEL" --max-results 50 --env production 2>&1 | tee "$OUTPUT_DIR/$(echo $MODEL | tr ' ' '_' | tr '[:upper:]' '[:lower:]').log"
  echo ""
  sleep 2  # Rate limit courtesy
done

echo "========================================"
echo "Scan complete. Results in $OUTPUT_DIR"
echo "========================================"
