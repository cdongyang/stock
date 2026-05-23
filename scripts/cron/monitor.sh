#!/bin/bash
# 每日监控任务：小米、腾讯音乐、中国政策、内存闪存、美以伊冲突
# 触发时间：每天 08:00

set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh

LOG_FILE="$LOG_DIR/monitor_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始每日监控任务（并行）===" >> "$LOG_FILE"

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

# memory-flash 和 us-israel-iran 由 monitor_frequent.sh 在交易日高频运行，此处不重复触发
run_monitor "xiaomi-monitor"        "监控小米集团最新事件，分析市场影响，更新 xiaomi/ 目录，发送飞书通知"        "$TMP1" &
PID1=$!
run_monitor "tencent-music-monitor" "监控腾讯音乐最新事件，分析市场影响，更新 tencent-music/ 目录，发送飞书通知" "$TMP2" &
PID2=$!
run_monitor "china-policy-monitor"  "监控中国最新政策变化，分析行业影响，更新 china-policy/ 目录，发送飞书通知"  "$TMP3" &
PID3=$!

wait "$PID1" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] xiaomi-monitor 执行失败" >> "$LOG_FILE"
wait "$PID2" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] tencent-music-monitor 执行失败" >> "$LOG_FILE"
wait "$PID3" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] china-policy-monitor 执行失败" >> "$LOG_FILE"

cat "$TMP1" "$TMP2" "$TMP3" >> "$LOG_FILE"
rm -f "$TMP1" "$TMP2" "$TMP3"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 每日监控任务完成 ===" >> "$LOG_FILE"
