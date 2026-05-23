#!/usr/bin/env python3
"""
飞书应用通知工具 — 可作为模块导入，也可直接命令行调用。

用法（CLI）:
    python3 feishu_notify.py --title "标题" --item "🟢 事件1" --item "🔴 事件2" --footer "备注"

用法（模块）:
    from scripts.feishu_notify import send_notification
    send_notification(title="标题", items=["🟢 事件1"], footer="备注")

配置（.env 或环境变量）:
    FEISHU_APP_ID           飞书应用 App ID
    FEISHU_APP_SECRET       飞书应用 App Secret
    FEISHU_RECEIVE_ID       接收者 ID（open_id / chat_id / user_id / email）
    FEISHU_RECEIVE_ID_TYPE  ID 类型，默认 open_id
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests

log = logging.getLogger(__name__)


# ── 配置加载 ──────────────────────────────────────────────

def _load_dotenv(env_path: Path) -> None:
    """简单 .env 解析，不依赖 python-dotenv。"""
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        return
    except ImportError:
        pass
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _get_config() -> dict[str, str]:
    return {
        "app_id":          os.environ.get("FEISHU_APP_ID", ""),
        "app_secret":      os.environ.get("FEISHU_APP_SECRET", ""),
        "receive_id":      os.environ.get("FEISHU_RECEIVE_ID", ""),
        "receive_id_type": os.environ.get("FEISHU_RECEIVE_ID_TYPE", "open_id"),
    }


# ── 飞书 API ──────────────────────────────────────────────

def _get_tenant_access_token(app_id: str, app_secret: str) -> str:
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"获取 tenant_access_token 失败: {data}")
    return data["tenant_access_token"]


def _build_post_content(
    title: str,
    items: list[str],
    footer: str,
) -> dict:
    """构造飞书 post 富文本 content 字段。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sep = [{"tag": "text", "text": "─" * 20}]

    rows = [
        [{"tag": "text", "text": f"🕐 {now}"}],
        sep,
    ]
    for item in items:
        rows.append([{"tag": "text", "text": item}])
    if items:
        rows.append(sep)
    if footer:
        rows.append([{"tag": "text", "text": footer}])

    return {"zh_cn": {"title": title, "content": rows}}


# ── 公开接口 ──────────────────────────────────────────────

def send_notification(
    title: str,
    items: list[str],
    footer: str = "",
    env_file: Path | None = None,
) -> bool:
    """
    发送飞书应用通知。

    Args:
        title:    消息标题，如 "📊 小米集团事件监控报告"
        items:    消息正文条目列表，如 ["🟢 SU7 Ultra交付", "🟡 市场份额持平"]
        footer:   底部附加说明，如 "📁 详情: ~/stock-analysis/xiaomi/"
        env_file: .env 文件路径，默认查找 CWD/.env

    Returns:
        True 表示发送成功，False 表示跳过或失败（不抛异常）。
    """
    _load_dotenv(env_file or Path.cwd() / ".env")
    cfg = _get_config()

    if not cfg["app_id"] or not cfg["app_secret"]:
        log.warning("FEISHU_APP_ID / FEISHU_APP_SECRET 未配置，跳过飞书通知")
        return False
    if not cfg["receive_id"]:
        log.warning("FEISHU_RECEIVE_ID 未配置，跳过飞书通知")
        return False

    try:
        token = _get_tenant_access_token(cfg["app_id"], cfg["app_secret"])
        content = _build_post_content(title, items, footer)
        payload = {
            "receive_id": cfg["receive_id"],
            "msg_type": "post",
            "content": json.dumps(content, ensure_ascii=False),
        }
        resp = requests.post(
            f"https://open.feishu.cn/open-apis/im/v1/messages"
            f"?receive_id_type={cfg['receive_id_type']}",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            log.info("飞书通知发送成功")
            return True
        log.error(f"飞书 API 返回错误: {data}")
        return False
    except Exception as e:
        log.error(f"飞书通知发送失败: {e}")
        return False


# ── CLI 入口 ──────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="发送飞书应用通知")
    p.add_argument("--title",   required=True, help="消息标题")
    p.add_argument("--item",    dest="items", action="append", default=[], metavar="TEXT",
                   help="正文条目（可重复）")
    p.add_argument("--footer",  default="", help="底部说明")
    p.add_argument("--env-file", type=Path, default=None, help=".env 文件路径")
    return p.parse_args()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = _parse_args()
    ok = send_notification(
        title=args.title,
        items=args.items,
        footer=args.footer,
        env_file=args.env_file,
    )
    sys.exit(0 if ok else 1)
