#!/usr/bin/env python3
"""
富途 OpenAPI — 订阅/取消订阅行情 (subscribe / unsubscribe)
文档: https://openapi.futunn.com/futu-api-doc/quote/sub.html

用法 (CLI):
    # 订阅经纪队列
    python3 subscribe.py --code HK.00700 --type BROKER

    # 订阅多只股票、多个类型
    python3 subscribe.py --code HK.00700 --code HK.09988 --type TICKER --type QUOTE

    # 取消订阅
    python3 subscribe.py --code HK.00700 --type BROKER --unsub

    # 取消所有订阅
    python3 subscribe.py --unsub-all

    # 订阅后直接拉取经纪队列（一体化操作）
    python3 subscribe.py --code HK.00700 --type BROKER --fetch-broker

用法 (模块):
    from scripts.api.subscribe import subscribe, unsubscribe
    ret, msg = subscribe(ctx, ["HK.00700"], ["BROKER"])
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

# 字符串 -> SubType 映射，方便 CLI 使用
SUBTYPE_MAP: dict[str, SubType] = {
    "QUOTE": SubType.QUOTE,
    "ORDER_BOOK": SubType.ORDER_BOOK,
    "TICKER": SubType.TICKER,
    "BROKER": SubType.BROKER,
    "RT_DATA": SubType.RT_DATA,
    "K_1M": SubType.K_1M,
    "K_5M": SubType.K_5M,
    "K_15M": SubType.K_15M,
    "K_30M": SubType.K_30M,
    "K_60M": SubType.K_60M,
    "K_DAY": SubType.K_DAY,
    "K_WEEK": SubType.K_WEEK,
    "K_MON": SubType.K_MON,
}


def subscribe(
    ctx: OpenQuoteContext,
    code_list: list[str],
    subtype_list: list[str],
    is_first_push: bool = True,
    subscribe_push: bool = True,
) -> tuple[int, str]:
    """订阅行情，subtype_list 传字符串（如 'BROKER'）或 SubType 枚举均可。"""
    subtypes = [SUBTYPE_MAP[s] if isinstance(s, str) else s for s in subtype_list]
    return ctx.subscribe(code_list, subtypes, is_first_push=is_first_push, subscribe_push=subscribe_push)


def unsubscribe(
    ctx: OpenQuoteContext,
    code_list: list[str],
    subtype_list: list[str],
) -> tuple[int, str]:
    """取消订阅行情。"""
    subtypes = [SUBTYPE_MAP[s] if isinstance(s, str) else s for s in subtype_list]
    return ctx.unsubscribe(code_list, subtypes)


def _fetch_broker(ctx: OpenQuoteContext, code: str) -> None:
    """订阅后拉取经纪队列并打印。"""
    ret, bid_df, ask_df = ctx.get_broker_queue(code)
    if ret != RET_OK:
        print(f"获取经纪队列失败: {bid_df}", file=sys.stderr)
        return

    print(f"\n=== {code} 经纪队列 ===")
    print("\n【买方队列 (Bid)】")
    print(bid_df.to_string(index=False) if not bid_df.empty else "  (无数据)")
    print("\n【卖方队列 (Ask)】")
    print(ask_df.to_string(index=False) if not ask_df.empty else "  (无数据)")


def main() -> None:
    parser = argparse.ArgumentParser(description="订阅/取消订阅富途行情")
    parser.add_argument("--code", action="append", dest="codes", metavar="CODE", help="股票代码，可重复指定多个")
    parser.add_argument(
        "--type", action="append", dest="types", metavar="TYPE",
        help=f"订阅类型，可选: {', '.join(SUBTYPE_MAP)}，可重复指定多个",
    )
    parser.add_argument("--unsub", action="store_true", help="取消订阅（默认为订阅）")
    parser.add_argument("--unsub-all", action="store_true", help="取消所有订阅")
    parser.add_argument("--fetch-broker", action="store_true", help="订阅后立即拉取经纪队列（需包含 BROKER 类型）")
    parser.add_argument("--no-push", action="store_true", help="订阅后不推送（仅主动拉取场景）")
    parser.add_argument("--host", default=DEFAULT_HOST, help="FutuOpenD 地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="FutuOpenD 端口")
    args = parser.parse_args()

    if args.unsub_all:
        ctx = OpenQuoteContext(host=args.host, port=args.port)
        try:
            ret, msg = ctx.unsubscribe_all()
            print("取消所有订阅成功" if ret == RET_OK else f"失败: {msg}")
        finally:
            ctx.close()
        return

    if not args.codes or not args.types:
        parser.error("--code 和 --type 为必填项（--unsub-all 除外）")

    invalid = [t for t in args.types if t not in SUBTYPE_MAP]
    if invalid:
        parser.error(f"未知订阅类型: {invalid}，可选: {list(SUBTYPE_MAP)}")

    ctx = OpenQuoteContext(host=args.host, port=args.port)
    try:
        if args.unsub:
            ret, msg = unsubscribe(ctx, args.codes, args.types)
            print("取消订阅成功" if ret == RET_OK else f"取消订阅失败: {msg}")
        else:
            ret, msg = subscribe(ctx, args.codes, args.types, subscribe_push=not args.no_push)
            if ret != RET_OK:
                print(f"订阅失败: {msg}", file=sys.stderr)
                sys.exit(1)
            print(f"订阅成功: {args.codes} -> {args.types}")

            if args.fetch_broker:
                for code in args.codes:
                    _fetch_broker(ctx, code)
    finally:
        ctx.close()


if __name__ == "__main__":
    main()
