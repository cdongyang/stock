#!/bin/bash
# 美股监控任务：Oklo + NuScale Power + Sandisk
# 触发时间：每天 21:00（美股 21:30 开盘前）

set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh
LOG_FILE="$LOG_DIR/monitor_us_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始美股监控任务（并行）===" >> "$LOG_FILE"

run_monitor() {
    local name="$1"
    local prompt="$2"
    local tmp="$3"
    {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动: $name"
        claude -p "$prompt" --model sonnet --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" 2>&1
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成: $name"
    } > "$tmp"
}

TMP1=$(mktemp)
TMP2=$(mktemp)
TMP3=$(mktemp)

run_monitor "oklo-monitor"    "监控 Oklo Inc（NYSE: OKLO）最新事件，分析市场影响，更新 oklo/ 目录，发送飞书通知"    "$TMP1" &
PID1=$!
run_monitor "nuscale-monitor" "监控 NuScale Power（NYSE: SMR）最新事件，分析市场影响，更新 nuscale/ 目录，发送飞书通知" "$TMP2" &
PID2=$!
run_monitor "sndk-monitor"    "监控 Sandisk（NASDAQ: SNDK）最新事件，分析市场影响，更新 events/sndk/ 目录，发送飞书通知" "$TMP3" &
PID3=$!

wait "$PID1" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] oklo-monitor 执行失败" >> "$LOG_FILE"
wait "$PID2" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] nuscale-monitor 执行失败" >> "$LOG_FILE"
wait "$PID3" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] sndk-monitor 执行失败" >> "$LOG_FILE"

cat "$TMP1" "$TMP2" "$TMP3" >> "$LOG_FILE"
rm -f "$TMP1" "$TMP2" "$TMP3"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 美股监控任务完成 ===" >> "$LOG_FILE"
