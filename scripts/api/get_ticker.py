#!/usr/bin/env python3
"""
富途 OpenAPI — 获取逐笔成交 (get_rt_ticker)
文档: https://openapi.futunn.com/futu-api-doc/quote/get-ticker.html

前置条件:
    1. 已启动 FutuOpenD 并完成登录
    2. 已订阅对应股票的 SubType.TICKER 行情

用法 (CLI):
    python3 get_ticker.py --code HK.00700
    python3 get_ticker.py --code US.AAPL --num 100 --host 127.0.0.1 --port 11111

用法 (模块):
    from scripts.api.get_ticker import get_rt_ticker
    df = get_rt_ticker("HK.00700", num=200)
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
DEFAULT_NUM = 500


def get_rt_ticker(
    code: str,
    num: int = DEFAULT_NUM,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
):
    """
    获取指定股票的逐笔成交记录。

    调用前需已订阅 SubType.TICKER，否则会自动订阅后再查询。
    最多返回最近 1000 条记录。

    Returns:
        DataFrame: 逐笔成交数据，失败时返回 None
    """
    ctx = OpenQuoteContext(host=host, port=port)
    try:
        ret, data = ctx.subscribe([code], [SubType.TICKER])
        if ret != RET_OK:
            print(f"订阅失败: {data}", file=sys.stderr)
            return None

        ret, df = ctx.get_rt_ticker(code, num=num)
        if ret != RET_OK:
            print(f"获取逐笔成交失败: {df}", file=sys.stderr)
            return None

        return df
    finally:
        ctx.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="获取富途逐笔成交数据")
    parser.add_argument("--code", required=True, help="股票代码，如 HK.00700 / US.AAPL")
    parser.add_argument("--num", type=int, default=DEFAULT_NUM, help="获取条数，最大 1000")
    parser.add_argument("--host", default=DEFAULT_HOST, help="FutuOpenD 地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="FutuOpenD 端口")
    args = parser.parse_args()

    df = get_rt_ticker(args.code, num=args.num, host=args.host, port=args.port)
    if df is None:
        sys.exit(1)

    print(f"\n=== {args.code} 逐笔成交（最近 {len(df)} 条）===")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
