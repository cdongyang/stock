#!/usr/bin/env python3
"""
飞书消息监听机器人

通过飞书长连接（WebSocket）监听机器人收到的消息，
将消息内容交给 `claude -p` 处理，并将结果回复给发送者。

运行方式：
    python3 scripts/feishu_bot.py

配置（.env）：
    FEISHU_APP_ID       飞书应用 App ID
    FEISHU_APP_SECRET   飞书应用 App Secret

飞书应用需开通权限：
    im:message              读取消息
    im:message:send_as_bot  发送消息
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

# ── 路径 & 配置 ────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
LOG_FILE = BASE_DIR / "xiaomi" / "bot.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def _load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / ".env")
APP_ID     = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")


# ── 飞书客户端 ────────────────────────────────────────────

def make_client() -> lark.Client:
    return (
        lark.Client.builder()
        .app_id(APP_ID)
        .app_secret(APP_SECRET)
        .log_level(lark.LogLevel.WARNING)
        .build()
    )


# ── 消息内容提取 ───────────────────────────────────────────

def extract_text(message: dict) -> str:
    """从飞书消息体中提取纯文本，支持 text / post 类型。"""
    msg_type = message.get("message_type", "")
    content_str = message.get("content", "{}")
    try:
        content = json.loads(content_str)
    except json.JSONDecodeError:
        return content_str

    if msg_type == "text":
        return content.get("text", "").strip()

    if msg_type == "post":
        # post 是富文本，提取所有 text tag 的内容
        parts = []
        zh = content.get("post", {}).get("zh_cn", content.get("zh_cn", {}))
        for row in zh.get("content", []):
            for item in row:
                if item.get("tag") == "text":
                    parts.append(item.get("text", ""))
        return " ".join(parts).strip()

    # 其他类型（图片、文件等）暂不处理
    return f"[不支持的消息类型: {msg_type}]"


# ── 调用 Claude ────────────────────────────────────────────

def run_claude(prompt: str) -> str:
    """调用 `claude -p` 处理消息，返回响应文本。"""
    log.info(f"调用 claude，prompt 长度: {len(prompt)}")
    try:
        result = subprocess.run(
            ["claude","--dangerously-skip-permissions", "-p", prompt],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            log.error(f"claude 退出码 {result.returncode}, stderr: {result.stderr[:300]}")
            if not output:
                return f"❌ claude 执行失败（退出码 {result.returncode}）"
        log.info(f"claude 响应长度: {len(output)}")
        return output or "（claude 未返回任何输出）"
    except subprocess.TimeoutExpired:
        log.error("claude 执行超时")
        return "❌ 处理超时（>5 分钟），请稍后重试"
    except FileNotFoundError:
        log.error("找不到 claude 命令")
        return "❌ 找不到 claude 命令，请确认已安装"


# ── 飞书消息回复 ───────────────────────────────────────────

def reply(client: lark.Client, message_id: str, text: str) -> None:
    """回复指定消息。文本超长时自动截断以避免 API 拒绝。"""
    # 飞书单条消息上限约 30000 字符
    MAX = 28000
    if len(text) > MAX:
        text = text[:MAX] + "\n\n…（内容已截断）"

    body = ReplyMessageRequestBody.builder() \
        .msg_type("text") \
        .content(json.dumps({"text": text}, ensure_ascii=False)) \
        .build()

    req = ReplyMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(body) \
        .build()

    resp = client.im.v1.message.reply(req)
    if not resp.success():
        log.error(f"回复失败: code={resp.code} msg={resp.msg}")
    else:
        log.info(f"已回复消息 {message_id}")


def send_to_chat(client: lark.Client, chat_id: str, text: str) -> None:
    """主动发送消息到指定 chat（用于发生错误时告知用户）。"""
    body = CreateMessageRequestBody.builder() \
        .receive_id(chat_id) \
        .msg_type("text") \
        .content(json.dumps({"text": text}, ensure_ascii=False)) \
        .build()

    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(body) \
        .build()

    client.im.v1.message.create(req)


# ── 已处理消息去重 ─────────────────────────────────────────
_processed_ids: set[str] = set()


# ── 事件处理 ───────────────────────────────────────────────

def on_message(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    """处理收到的消息事件。"""
    client = make_client()
    msg    = data.event.message
    sender = data.event.sender

    message_id = msg.message_id
    chat_id    = msg.chat_id
    sender_id  = sender.sender_id.open_id if sender.sender_id else "unknown"

    # 忽略重复投递
    if message_id in _processed_ids:
        log.info(f"跳过重复消息 {message_id}")
        return
    _processed_ids.add(message_id)

    # 忽略机器人自己发的消息（防循环）
    if sender.sender_type == "bot":
        return

    text = extract_text({"message_type": msg.message_type, "content": msg.content})
    if not text or text.startswith("[不支持"):
        log.info(f"跳过不支持的消息类型，message_id={message_id}")
        return

    log.info(f"收到消息 [{message_id}] from {sender_id}: {text[:80]}")

    # 调用 claude 并回复结果
    response = run_claude(text)
    reply(client, message_id, response)


# ── 主入口 ─────────────────────────────────────────────────

def main() -> None:
    if not APP_ID or not APP_SECRET:
        log.error("请在 .env 中配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        sys.exit(1)

    log.info(f"启动飞书机器人 (App ID: {APP_ID[:8]}…)")
    log.info(f"工作目录: {BASE_DIR}")
    log.info("等待消息中…（Ctrl+C 退出）")

    handler = (
        lark.EventDispatcherHandler.builder(
            lark.ENCRYPT_KEY,
            lark.VERIFICATION_TOKEN,
        )
        .register_p2_im_message_receive_v1(on_message)
        .build()
    )

    ws_client = lark.ws.Client(
        APP_ID,
        APP_SECRET,
        event_handler=handler,
        log_level=lark.LogLevel.WARNING,
    )
    ws_client.start()


if __name__ == "__main__":
    main()
