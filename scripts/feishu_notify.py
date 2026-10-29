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

import urllib.request
import urllib.error

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

def _http_post(url: str, payload: dict, headers: dict | None = None) -> dict:
    import ssl
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_tenant_access_token(app_id: str, app_secret: str) -> str:
    data = _http_post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        {"app_id": app_id, "app_secret": app_secret},
    )
    if data.get("code") != 0:
        raise RuntimeError(f"获取 tenant_access_token 失败: {data}")
    return data["tenant_access_token"]


def _build_post_content(
    title: str,
    items: list[str],
    footer: str,
    entries: list[str] | None = None,
) -> dict:
    """构造飞书 post 富文本 content 字段。

    entries 支持两种前缀：
      - "event:🟢 标题"   → 事件标题行（前置分隔线）
      - "detail:说明文字" → 缩进的详情行（  · 前缀）
      无前缀则作为普通行处理。
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sep = [{"tag": "text", "text": "─" * 20}]

    rows = [
        [{"tag": "text", "text": f"🕐 {now}"}],
        sep,
    ]

    # 摘要行（--item，始终在顶部）
    for item in items:
        rows.append([{"tag": "text", "text": item}])

    # 详细事件块（--entry）
    if entries:
        for entry in entries:
            if entry.startswith("event:"):
                text = entry[len("event:"):]
                rows.append(sep)
                rows.append([{"tag": "text", "text": text}])
            elif entry.startswith("detail:"):
                text = entry[len("detail:"):]
                rows.append([{"tag": "text", "text": f"  · {text}"}])
            else:
                rows.append([{"tag": "text", "text": entry}])
    else:
        if items:
            rows.append(sep)

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
    entries: list[str] | None = None,
) -> bool:
    """
    发送飞书应用通知。

    Args:
        title:    消息标题，如 "📊 小米集团事件监控报告"
        items:    顶部摘要行，如 ["发现 3 个新事件，跳过 1 个重复"]
        footer:   底部附加说明，如 "📁 详情: ~/stock-analysis/xiaomi/"
        env_file: .env 文件路径，默认查找 CWD/.env
        entries:  富文本事件块，每条以 "event:" 或 "detail:" 开头：
                    ["event:🟢 SU7 Ultra交付", "detail:首批交付2000辆", "detail:预计拉动Q2营收"]

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
        content = _build_post_content(title, items, footer, entries)
        payload = {
            "receive_id": cfg["receive_id"],
            "msg_type": "post",
            "content": json.dumps(content, ensure_ascii=False),
        }
        data = _http_post(
            f"https://open.feishu.cn/open-apis/im/v1/messages"
            f"?receive_id_type={cfg['receive_id_type']}",
            payload,
            headers={"Authorization": f"Bearer {token}"},
        )
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
                   help="顶部摘要行（可重复）")
    p.add_argument("--entry",   dest="entries", action="append", default=[], metavar="TEXT",
                   help='富文本事件条目（可重复）。前缀 "event:" 为事件标题，"detail:" 为缩进详情行')
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
        entries=args.entries or None,
    )
    sys.exit(0 if ok else 1)
