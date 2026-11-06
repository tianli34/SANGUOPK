# 文件名: main.py
# 用途: 程序主入口文件，运行武将对决模拟并生成战斗报告
"""三国武将对决模拟入口"""

import argparse
import sys

from src import Warrior, BattleEngine
from src.battle_report import AggregateReporter, BattleReporter

# 双方武将的默认配置
DEFAULT_WARRIORS = {
    "a": {
        "name": "马超",
        "martialarts": 98,
        "agility": 95,
        "strength": 92,
        "courage": 94,
        "sp": 98,
    },
    "b": {
        "name": "许褚",
        "martialarts": 95,
        "agility": 80,
        "strength": 99,
        "courage": 96,
        "sp": 100,
    },
}

STAT_FIELDS = ("martialarts", "agility", "strength", "courage", "sp")

STAT_LABELS = {
    "martialarts": "武艺",
    "agility": "敏捷",
    "strength": "力量",
    "courage": "胆气",
    "sp": "体力",
}


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器"""
    parser = argparse.ArgumentParser(description="三国武将对决模拟")
    parser.add_argument("-n", "--battles", type=int, default=1, help="模拟场次（默认 1）")

    for side, defaults in DEFAULT_WARRIORS.items():
        prefix = side.upper()
        parser.add_argument(
            f"--{side}-name", default=defaults["name"], help=f"{prefix}队武将名"
        )
        for field in STAT_FIELDS:
            parser.add_argument(
                f"--{side}-{field}",
                type=int,
                default=defaults[field],
                help=f"{prefix}队 {STAT_LABELS[field]}（默认 {defaults[field]}）",
            )

    return parser


def create_warrior(args: argparse.Namespace, side: str) -> Warrior:
    """根据命令行参数创建武将"""
    return Warrior(
        getattr(args, f"{side}_name"),
        side.upper(),
        **{field: getattr(args, f"{side}_{field}") for field in STAT_FIELDS},
    )


def main() -> None:
    """运行单挑模拟"""
    # Windows 默认 GBK 无法输出 ▶⚔☠ 等符号，统一使用 UTF-8
    # 必须在解析参数前设置，否则 -h 帮助信息仍会使用 GBK
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args()
    if args.battles < 1:
        parser.error("--battles 必须大于等于 1")

    print(f"三国武将对决系统 - {args.battles}场单挑模拟")
    print("=" * 70)

    # 每场战斗都需要全新的武将实例，先保存初始快照用于汇总战报
    original_a = create_warrior(args, "a")
    original_b = create_warrior(args, "b")
    snapshot_a = original_a.snapshot()
    snapshot_b = original_b.snapshot()

    if args.battles == 1:
        # 单场战报
        reporter = BattleReporter([original_a], [original_b])
        engine = BattleEngine([original_a], [original_b])
        result = engine.run()
        print(reporter.generate_full_report(result))
        return

    # 多场汇总战报
    print("模拟进行中...")
    reporter = AggregateReporter(original_a.name, original_b.name)

    for i in range(args.battles):
        engine = BattleEngine([create_warrior(args, "a")], [create_warrior(args, "b")])
        result = engine.run()
        reporter.add_battle_result(result)

        if (i + 1) % 10 == 0:
            print(f"  已完成 {i + 1}/{args.battles} 场...")

    print()
    print(reporter.generate_aggregate_report([snapshot_a], [snapshot_b]))


if __name__ == "__main__":
    main()
