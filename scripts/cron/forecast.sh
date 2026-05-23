#!/bin/bash
# 每日股价预测任务：小米 + 腾讯音乐
# 触发时间：交易日 09:00（港股 09:30 开盘前）

set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh
LOG_FILE="$LOG_DIR/forecast_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

# 跳过周末（港股/美股均不开市）
DAY_OF_WEEK=$(date +%u)  # 1=Mon ... 7=Sun
if [ "$DAY_OF_WEEK" -ge 6 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 今日为周末，跳过股价预测" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始股价预测任务 ===" >> "$LOG_FILE"

claude -p "结合项目内小米、腾讯音乐、中国政策的最新研究数据，预测今日小米集团（01810.HK）和腾讯音乐（1698.HK）的股价走势，给出预估涨跌区间和判断依据，保存预测结果，发送飞书通知" \
    --model sonnet --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" \
    >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 股价预测任务完成 ===" >> "$LOG_FILE"
