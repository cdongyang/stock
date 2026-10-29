#!/bin/bash
set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh
LOG_FILE="$LOG_DIR/morning_hi_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 早安问候 ===" >> "$LOG_FILE"
claude -p "hi" --model haiku 2>&1 >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 完成 ===" >> "$LOG_FILE"
