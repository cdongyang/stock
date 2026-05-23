#!/usr/bin/env python3
"""
小米集团事件监控 + 飞书通知脚本

每次运行：
1. 调用 claude 执行小米事件监控 skill
2. 对比运行前后的 analyzed_events.json，提取本次新增事件
3. 通过 feishu_notify 发送飞书应用通知

飞书配置见 .env（参考 scripts/.env.example）。
"""

import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent  # stock-analysis/
XIAOMI_DIR = BASE_DIR / "xiaomi"
EVENTS_JSON = XIAOMI_DIR / "analyzed_events.json"
LOG_FILE = XIAOMI_DIR / "monitor.log"

# ── 日志配置 ──────────────────────────────────────────────
XIAOMI_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── 导入飞书通知模块 ──────────────────────────────────────
sys.path.insert(0, str(BASE_DIR))
from scripts.feishu_notify import send_notification


def load_events() -> list[dict]:
    """读取 analyzed_events.json；文件不存在时返回空列表。"""
    if not EVENTS_JSON.exists():
        return []
    try:
        return json.loads(EVENTS_JSON.read_text(encoding="utf-8")).get("events", [])
    except Exception as e:
        log.warning(f"读取 analyzed_events.json 失败: {e}")
        return []


def run_claude() -> tuple[bool, str]:
    """运行 claude 监控命令，返回 (成功?, 输出文本)。"""
    cmd = ["claude", "-p", "监控分析近期小米集团的重要事件，存储到 xiaomi 目录"]
    log.info(f"执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            log.error(f"claude 返回非零退出码 {result.returncode}")
            log.error(f"stderr: {result.stderr[:500]}")
            return False, result.stdout
        log.info("claude 执行完成")
        return True, result.stdout
    except subprocess.TimeoutExpired:
        log.error("claude 执行超时（>10 分钟）")
        return False, ""
    except FileNotFoundError:
        log.error("找不到 claude 命令，请确认已安装并在 PATH 中")
        return False, ""


def impact_emoji(rating: str) -> str:
    r = rating.lower()
    if "positive" in r:
        return "🟢"
    if "negative" in r:
        return "🔴"
    if "neutral" in r:
        return "🟡"
    return "⚪"


def main():
    log.info("=" * 50)
    log.info("小米事件监控开始")

    # 1. 记录运行前事件数
    count_before = len(load_events())
    log.info(f"运行前已有事件数: {count_before}")

    # 2. 运行 claude
    success, output = run_claude()

    # 3. 提取新增事件
    new_events = load_events()[count_before:]
    log.info(f"本次新增事件数: {len(new_events)}")

    # 尝试从输出中解析跳过数量
    skipped = 0
    for line in output.splitlines():
        m = re.search(r"跳过\s*(\d+)\s*个", line)
        if m:
            skipped = int(m.group(1))
            break

    # 4. 组装飞书通知内容
    if not success:
        title = "❌ 小米集团事件监控失败"
        items = ["监控执行出错，请检查日志"]
        footer = f"📁 日志: {LOG_FILE}"
    elif not new_events:
        title = "📊 小米集团事件监控报告"
        items = [f"✅ 今日无新事件（已跳过 {skipped} 个重复）"]
        footer = ""
    else:
        header = f"发现 {len(new_events)} 个新事件" + (f"，跳过 {skipped} 个重复" if skipped else "")
        title = "📊 小米集团事件监控报告"
        items = [header, "─" * 20] + [
            f"{impact_emoji(e.get('impact_rating', ''))} {e.get('title', '（无标题）')}"
            for e in new_events
        ]
        footer = "📁 详情: ~/stock-analysis/xiaomi/"

    # 5. 发送飞书通知
    send_notification(title=title, items=items, footer=footer, env_file=BASE_DIR / ".env")

    log.info("小米事件监控结束")
    log.info("=" * 50)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
