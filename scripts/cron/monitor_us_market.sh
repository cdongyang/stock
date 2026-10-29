#!/bin/bash
# 美股大型事件监控：宏观数据 + 美联储 + 政策/地缘 + 市场异动
# 触发时间：工作日 18:00（美股开盘前 3.5 小时）

set -euo pipefail

source /Users/dy.chen/Personal/stock/scripts/env.sh
LOG_FILE="$LOG_DIR/monitor_us_market_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始美股大型事件监控 ===" >> "$LOG_FILE"

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动: us-market-monitor"
    claude -p "监控影响美股的大型事件（宏观数据、美联储政策、重大政策/地缘事件、金融市场异动），分析各板块受益/受压情况，发送飞书通知" \
        --model sonnet \
        --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成: us-market-monitor"
} >> "$LOG_FILE" || echo "[$(date '+%Y-%m-%d %H:%M:%S')] us-market-monitor 执行失败" >> "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 美股大型事件监控完成 ===" >> "$LOG_FILE"
