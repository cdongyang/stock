#!/bin/bash
# 每日预测复盘任务：对比预测与实际走势
# 触发时间：交易日 18:00（港股 16:00 收盘、美股盘前）

set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh

LOG_FILE="$LOG_DIR/review_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

# 跳过周末
DAY_OF_WEEK=$(date +%u)
if [ "$DAY_OF_WEEK" -ge 6 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 今日为周末，跳过预测复盘" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始预测复盘任务 ===" >> "$LOG_FILE"

claude -p "复盘今日小米集团和腾讯音乐的股价预测结果，对比实际收盘价与预测区间，打分评级，如有偏差请反思原因，保存复盘记录，发送飞书通知" \
    --model sonnet --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" \
    >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 预测复盘任务完成 ===" >> "$LOG_FILE"
