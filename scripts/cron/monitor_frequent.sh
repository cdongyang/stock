#!/bin/bash
# 高频监控任务：内存闪存 + 美以伊冲突
# 触发时间：交易日 08:00 / 10:20 / 11:20 / 12:20 / 13:20 / 14:20 / 15:20 / 20:00 / 21:20 / 22:20 / 23:20 / 1:20 / 2:20 / 3:20 

set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh
LOG_FILE="$LOG_DIR/monitor_frequent_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始高频监控（内存闪存 + 美以伊，并行）===" >> "$LOG_FILE"

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

run_monitor "memory-flash-monitor"   "监控全球内存闪存行业最新动态，分析市场影响，发送飞书通知"    "$TMP1" &
PID1=$!
run_monitor "us-israel-iran-monitor" "监控美以伊最新冲突动态，分析对市场的影响，发送飞书通知" "$TMP2" &
PID2=$!

wait "$PID1" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-flash-monitor 执行失败" >> "$LOG_FILE"
wait "$PID2" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] us-israel-iran-monitor 执行失败" >> "$LOG_FILE"

cat "$TMP1" "$TMP2" >> "$LOG_FILE"
rm -f "$TMP1" "$TMP2"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 高频监控完成 ===" >> "$LOG_FILE"
