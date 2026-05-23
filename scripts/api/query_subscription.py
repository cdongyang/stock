#!/usr/bin/env python3
"""
富途 OpenAPI — 查询订阅状态 (query_subscription)
文档: https://openapi.futunn.com/futu-api-doc/quote/query-subscription.html

用法 (CLI):
    python3 query_subscription.py
    python3 query_subscription.py --own-only --host 127.0.0.1 --port 11111

用法 (模块):
    from scripts.api.query_subscription import query_subscription
    info = query_subscription()  # 返回所有连接的订阅状态
"""

from __future__ import annotations

import argparse
import json
import sys

try:
    from futu import OpenQuoteContext, RET_OK
except ImportError:
    print("错误: 未安装 futu-py，请先执行 pip install futu-api", file=sys.stderr)
    sys.exit(1)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11111


def query_subscription(
    is_all_conn: bool = True,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> dict | None:
    """
    查询当前行情订阅状态及配额使用情况。

    Args:
        is_all_conn: True 返回所有连接的订阅状态，False 只返回当前连接

    Returns:
        dict: {total_used, own_used, remain, sub_list}，失败时返回 None
    """
    ctx = OpenQuoteContext(host=host, port=port)
    try:
        ret, data = ctx.query_subscription(is_all_conn=is_all_conn)
        if ret != RET_OK:
            print(f"查询订阅失败: {data}", file=sys.stderr)
            return None
        return data
    finally:
        ctx.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="查询富途行情订阅状态")
    parser.add_argument("--own-only", action="store_true", help="只查询当前连接的订阅（默认查所有连接）")
    parser.add_argument("--host", default=DEFAULT_HOST, help="FutuOpenD 地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="FutuOpenD 端口")
    args = parser.parse_args()

    data = query_subscription(is_all_conn=not args.own_only, host=args.host, port=args.port)
    if data is None:
        sys.exit(1)

    print(f"已用配额（全部连接）: {data.get('total_used')}")
    print(f"已用配额（当前连接）: {data.get('own_used')}")
    print(f"剩余配额            : {data.get('remain')}")
    print(f"订阅列表:\n{json.dumps(data.get('sub_list', {}), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
