# 文件名: main.py
# 用途: 程序主入口文件，运行武将对决模拟并生成战斗报告
"""示例战斗模拟 - 100次单挑统计"""

from src import Warrior, BattleEngine
from src.battle_report import AggregateReporter


def create_warrior_a():
    """创建A队武将"""
    return Warrior(
        "马超", "A", martial_arts=98, agility=95, strength=92, courage=94, sp=98
    )


def create_warrior_b():
    """创建B队武将"""
    return Warrior(
        "许褚", "B", martial_arts=95, agility=80, strength=99, courage=96, sp=100
    )


def main():
    """运行单挑模拟"""
    num_battles = 1

    print(f"三国武将对决系统 - {num_battles}场单挑模拟")
    print("=" * 70)

    # 创建原始武将用于记录初始属性
    original_a = create_warrior_a()
    original_b = create_warrior_b()

    # 保存初始快照
    snapshot_a = original_a.snapshot()
    snapshot_b = original_b.snapshot()

    if num_battles == 1:
        # 单场战报
        warrior_a = create_warrior_a()
        warrior_b = create_warrior_b()
        from src.battle_report import BattleReporter

        reporter = BattleReporter([warrior_a], [warrior_b])
        engine = BattleEngine([warrior_a], [warrior_b])
        result = engine.run()
        print(reporter.generate_full_report(result))
    else:
        # 总战报
        print("模拟进行中...")
        reporter = AggregateReporter(original_a.name, original_b.name)

        for i in range(num_battles):
            warrior_a = create_warrior_a()
            warrior_b = create_warrior_b()
            engine = BattleEngine([warrior_a], [warrior_b])
            result = engine.run()
            reporter.add_battle_result(result)

            if (i + 1) % 10 == 0:
                print(f"  已完成 {i + 1}/{num_battles} 场...")

        print()
        print(reporter.generate_aggregate_report([snapshot_a], [snapshot_b]))


if __name__ == "__main__":
    main()
