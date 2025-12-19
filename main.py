"""示例战斗模拟 - 100次单挑统计"""
from src import Warrior, BattleEngine
from src.battle_report import AggregateReporter, take_snapshot
from src.constants import MAX_HP


def create_warrior_a():
    """创建A队武将"""
    return Warrior("马超", "A", martial_arts=98, agility=95, strength=92, courage=94, sp=98)


def create_warrior_b():
    """创建B队武将"""
    return Warrior("许褚", "B", martial_arts=95, agility=80, strength=99, courage=96, sp=100)


def reset_warrior(warrior: Warrior, original: Warrior) -> None:
    """重置武将状态到初始值"""
    warrior.hp = MAX_HP
    warrior.sp = original.sp_max
    warrior.sp_max = original.sp_max
    warrior.courage = original.courage
    warrior.ap = 0.0
    warrior.is_alive = True


def main():
    """运行100次单挑并生成总战报"""
    print("三国武将对决系统 - 100次单挑模拟")
    print("=" * 70)
    print("模拟进行中...")
    
    # 创建原始武将用于记录初始属性
    original_a = create_warrior_a()
    original_b = create_warrior_b()
    
    # 保存初始快照
    snapshot_a = take_snapshot(original_a)
    snapshot_b = take_snapshot(original_b)
    
    # 创建总战报生成器
    reporter = AggregateReporter(original_a.name, original_b.name)
    
    # 运行100次单挑
    num_battles = 100
    for i in range(num_battles):
        # 每次创建新武将确保状态完全重置
        warrior_a = create_warrior_a()
        warrior_b = create_warrior_b()
        
        # 运行战斗
        engine = BattleEngine([warrior_a], [warrior_b])
        result = engine.run()
        
        # 添加结果到统计
        reporter.add_battle_result(result)
        
        # 进度显示
        if (i + 1) % 10 == 0:
            print(f"  已完成 {i + 1}/{num_battles} 场...")
    
    print()
    # 输出总战报
    print(reporter.generate_aggregate_report([snapshot_a], [snapshot_b]))


if __name__ == "__main__":
    main()
