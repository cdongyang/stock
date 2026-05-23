#!/usr/bin/env python3
"""
富途 OpenAPI — 获取经纪队列 (get_broker_queue)
文档: https://openapi.futunn.com/futu-api-doc/quote/get-broker.html

前置条件:
    1. 已启动 FutuOpenD 并完成登录
    2. 已订阅对应股票的 SubType.BROKER 行情

用法 (CLI):
    python3 get_broker.py --code HK.00700
    python3 get_broker.py --code US.AAPL --host 127.0.0.1 --port 11111

用法 (模块):
    from scripts.api.get_broker import get_broker_queue
    bid_df, ask_df = get_broker_queue("HK.00700")
"""

from __future__ import annotations

import argparse
import sys

try:
    from futu import OpenQuoteContext, SubType, RET_OK
except ImportError:
    print("错误: 未安装 futu-py，请先执行 pip install futu-api", file=sys.stderr)
    sys.exit(1)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11111


def get_broker_queue(
    code: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> tuple:
    """
    获取指定股票的经纪队列数据。

    调用前需已订阅 SubType.BROKER，否则会自动订阅后再查询。

    Returns:
        (bid_df, ask_df): 买方/卖方经纪队列 DataFrame，失败时返回 (None, None)
    """
    ctx = OpenQuoteContext(host=host, port=port)
    try:
        # 确保已订阅 BROKER 行情
        ret, data = ctx.subscribe([code], [SubType.BROKER])
        if ret != RET_OK:
            print(f"订阅失败: {data}", file=sys.stderr)
            return None, None

        ret, bid_df, ask_df = ctx.get_broker_queue(code)
        if ret != RET_OK:
            print(f"获取经纪队列失败: {bid_df}", file=sys.stderr)
            return None, None

        return bid_df, ask_df
    finally:
        ctx.close()


def _print_result(code: str, bid_df, ask_df) -> None:
    print(f"\n=== {code} 经纪队列 ===")

    print("\n【买方队列 (Bid)】")
    if bid_df is not None and not bid_df.empty:
        print(bid_df.to_string(index=False))
    else:
        print("  (无数据)")

    print("\n【卖方队列 (Ask)】")
    if ask_df is not None and not ask_df.empty:
        print(ask_df.to_string(index=False))
    else:
        print("  (无数据)")


def main() -> None:
    parser = argparse.ArgumentParser(description="获取富途经纪队列数据")
    parser.add_argument("--code", required=True, help="股票代码，如 HK.00700 / US.AAPL")
    parser.add_argument("--host", default=DEFAULT_HOST, help="FutuOpenD 地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="FutuOpenD 端口")
    args = parser.parse_args()

    bid_df, ask_df = get_broker_queue(args.code, host=args.host, port=args.port)
    if bid_df is None and ask_df is None:
        sys.exit(1)

    _print_result(args.code, bid_df, ask_df)


if __name__ == "__main__":
    main()
