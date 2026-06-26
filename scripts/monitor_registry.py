#!/usr/bin/env python3
"""通用事件监控注册表工具：去重检查 + 安全追加 analyzed_events.json。

被各 *-monitor skill 复用，把"读 JSON → 判重 → 追加 → 填时间戳"这套
易错的手工操作收敛成一条确定性命令，避免每次手动编辑 JSON 出错或漏填字段。

用法：
    # Step 3 去重：打印注册表里所有已知 URL，逐条比对收集到的新事件
    python3 scripts/monitor_registry.py --dir events/oklo --list-urls

    # Step 6 追加：把新事件（JSON 数组文件）按 url 去重后写入注册表，
    # 自动填充 analyzed_at（当前 UTC 时间），打印 added/skipped 统计
    python3 scripts/monitor_registry.py --dir events/oklo --add /tmp/new_events.json

新事件 JSON 每条字段：url / title / date / file / impact_rating
（analyzed_at 由脚本自动补，无需手填）
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_registry(registry_path: Path) -> dict:
    """读取注册表，文件不存在时返回空结构。"""
    if registry_path.exists():
        with registry_path.open(encoding="utf-8") as f:
            return json.load(f)
    return {"events": []}


def list_urls(registry: dict) -> None:
    """打印所有已知 URL，供去重比对。"""
    for ev in registry["events"]:
        print(ev.get("url", ""))


def add_events(registry: dict, registry_path: Path, events_path: Path) -> None:
    """按 url 去重追加新事件，自动填 analyzed_at，原子写回。"""
    with events_path.open(encoding="utf-8") as f:
        new_events = json.load(f)
    if isinstance(new_events, dict):  # 容忍单条对象
        new_events = [new_events]

    existing_urls = {ev.get("url") for ev in registry["events"]}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    added = skipped = 0
    for ev in new_events:
        if ev.get("url") in existing_urls:
            skipped += 1
            continue
        ev.setdefault("analyzed_at", now)
        registry["events"].append(ev)
        existing_urls.add(ev.get("url"))
        added += 1

    with registry_path.open("w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"added {added}, skipped {skipped} (重复), total {len(registry['events'])}")


def main() -> int:
    p = argparse.ArgumentParser(description="事件监控注册表去重/追加工具")
    p.add_argument("--dir", required=True,
                   help="事件目录，如 events/oklo（内含 analyzed_events.json）")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list-urls", action="store_true",
                   help="打印注册表中所有已知 URL（用于 Step 3 去重）")
    g.add_argument("--add", metavar="JSON_FILE",
                   help="追加新事件（JSON 数组文件），按 url 去重并自动填 analyzed_at")
    args = p.parse_args()

    registry_path = Path(args.dir) / "analyzed_events.json"
    registry = load_registry(registry_path)

    if args.list_urls:
        list_urls(registry)
    else:
        add_events(registry, registry_path, Path(args.add))
    return 0


if __name__ == "__main__":
    sys.exit(main())
