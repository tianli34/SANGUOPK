"""战报输出模块"""
from typing import List, Dict, TYPE_CHECKING
from dataclasses import dataclass, field
from collections import defaultdict

if TYPE_CHECKING:
    from src.warrior import Warrior
    from src.battle_engine import BattleResult, BattleLog


@dataclass
class BattleSummary:
    """单场战斗摘要（用于总战报统计）"""
    winner_team: str  # "A", "B", 或 None
    rounds: int
    ticks: int
    # 防御统计: {武将名: {防御类型: (使用次数, 成功次数)}}
    defense_usage: Dict[str, Dict[str, tuple]]
    # 拼刀统计
    clash_count: int
    clash_damage: Dict[str, float]  # 武将名 -> 拼刀受伤
    clash_sp_cost: Dict[str, float]  # 武将名 -> 拼刀体力消耗
    # 伤害统计
    total_damage: Dict[str, float]  # 武将名 -> 总受伤


@dataclass 
class AggregateStats:
    """100次单挑的汇总统计"""
    total_battles: int = 0
    team_a_wins: int = 0
    team_b_wins: int = 0
    draws: int = 0
    total_rounds: int = 0
    total_ticks: int = 0
    
    # 防御统计: {武将名: {防御类型: [使用次数, 成功次数]}}
    defense_stats: Dict[str, Dict[str, List[int]]] = field(default_factory=dict)
    
    # 拼刀统计
    total_clashes: int = 0
    warrior_clash_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    warrior_clash_damage: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    warrior_clash_sp_cost: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    
    # 伤害统计
    warrior_total_damage: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    
    # 新增：每种防御方式的伤害统计 {武将名: {防御类型: [受到伤害, 造成伤害]}}
    defense_damage_stats: Dict[str, Dict[str, List[float]]] = field(default_factory=dict)
    
    # 新增：攻击时受到的伤害（反击/反震）
    warrior_attack_damage_taken: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    
    # 新增：单次攻击伤害统计（不含拼刀）{武将名: [最高伤害, 最低伤害]}
    warrior_attack_damage_range: Dict[str, List[float]] = field(default_factory=dict)
    
    # 新增：回合数统计
    min_rounds: int = 999999
    max_rounds: int = 0
    
    # 新增：胜方HP/SP统计 - 按队伍分别统计
    team_a_winner_hp: List[float] = field(default_factory=list)
    team_a_winner_sp: List[float] = field(default_factory=list)
    team_a_winner_courage: List[int] = field(default_factory=list)
    team_b_winner_hp: List[float] = field(default_factory=list)
    team_b_winner_sp: List[float] = field(default_factory=list)
    team_b_winner_courage: List[int] = field(default_factory=list)
    
    # 新增：负方SP统计（阵亡时）- 按队伍分别统计
    team_a_loser_sp: List[float] = field(default_factory=list)
    team_a_loser_courage: List[int] = field(default_factory=list)
    team_b_loser_sp: List[float] = field(default_factory=list)
    team_b_loser_courage: List[int] = field(default_factory=list)
    
    # 新增：回合内多次攻击统计
    multi_attack_rounds: int = 0


# 防御类型中文映射
DEFENSE_TYPE_CN = {
    "block": "格挡",
    "parry": "卸力",
    "dodge": "闪避",
    "counter": "反击"
}

# 所有防御类型
ALL_DEFENSE_TYPES = ["block", "parry", "dodge", "counter"]


@dataclass
class DefenseStats:
    """单个防御类型的统计数据"""
    use_count: int = 0           # 使用次数
    success_count: int = 0       # 成功次数
    total_damage_taken: float = 0.0   # 受到的总伤害
    total_damage_dealt: float = 0.0   # 造成的总伤害（反击）


@dataclass
class WarriorDefenseStats:
    """武将防御统计"""
    warrior_name: str
    total_defenses: int = 0      # 总防御次数
    total_rounds: int = 0        # 总回合数
    defense_stats: Dict[str, DefenseStats] = field(default_factory=dict)
    
    def __post_init__(self):
        # 初始化所有防御类型的统计
        for defense_type in ALL_DEFENSE_TYPES:
            if defense_type not in self.defense_stats:
                self.defense_stats[defense_type] = DefenseStats()


@dataclass
class WarriorAttackStats:
    """武将攻击统计"""
    warrior_name: str
    attack_count: int = 0        # 攻击次数
    attack_ticks: List[int] = field(default_factory=list)  # 攻击发生的tick列表
    total_ticks: int = 0         # 战斗总tick数
    
    @property
    def avg_attack_interval(self) -> float:
        """计算平均攻击间隔（tick）"""
        if len(self.attack_ticks) < 2:
            return 0.0
        intervals = [self.attack_ticks[i+1] - self.attack_ticks[i] 
                     for i in range(len(self.attack_ticks) - 1)]
        return sum(intervals) / len(intervals) if intervals else 0.0


@dataclass
class ClashRecord:
    """单次拼刀记录"""
    round_num: int               # 回合数
    tick: int                    # 发生的tick
    participants: List[str]      # 参与者名称
    damages: Dict[str, float]    # 武将名 -> 受到的伤害
    sp_costs: Dict[str, float]   # 武将名 -> 体力消耗


@dataclass
class ClashStats:
    """拼刀统计"""
    total_clashes: int = 0                              # 总拼刀次数
    clash_records: List[ClashRecord] = field(default_factory=list)  # 每次拼刀记录
    warrior_clash_damage: Dict[str, float] = field(default_factory=lambda: defaultdict(float))  # 武将拼刀总受伤
    warrior_clash_sp_cost: Dict[str, float] = field(default_factory=lambda: defaultdict(float))  # 武将拼刀总体力消耗
    warrior_clash_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))  # 武将参与拼刀次数


@dataclass
class WarriorSnapshot:
    """武将状态快照"""
    name: str
    team: str
    hp: float
    sp: float
    sp_max: int
    courage: int
    is_alive: bool
    # 基础属性
    martial_arts: int
    agility: int
    strength: int


def take_snapshot(warrior: "Warrior") -> WarriorSnapshot:
    """获取武将当前状态快照"""
    return WarriorSnapshot(
        name=warrior.name,
        team=warrior.team,
        hp=warrior.hp,
        sp=warrior.sp,
        sp_max=warrior.sp_max,
        courage=warrior.courage,
        is_alive=warrior.is_alive,
        martial_arts=warrior.martial_arts,
        agility=warrior.agility,
        strength=warrior.strength
    )


def format_warrior_initial_stats(snapshot: WarriorSnapshot) -> str:
    """格式化武将初始属性（从快照）"""
    from src.constants import SP_EXPANSION_FACTOR
    # 计算属性需要根据快照数据计算
    attack_power = snapshot.strength * 1.5 + snapshot.martial_arts * 0.5
    defense_power = snapshot.strength * 0.5 + snapshot.sp_max * 0.01
    sp_ratio = min(1.0, (snapshot.sp / snapshot.sp_max) / 0.5)
    attack_speed = (100 + snapshot.agility * 2) * sp_ratio
    sp_display = snapshot.sp_max / SP_EXPANSION_FACTOR
    
    return (
        f"  【{snapshot.name}】\n"
        f"    四维属性: 武艺={snapshot.martial_arts} 敏捷={snapshot.agility} "
        f"力量={snapshot.strength} 胆气={snapshot.courage} 体力={sp_display:.0f}\n"
        f"    战斗属性: HP={snapshot.hp:.0f} SP={snapshot.sp:.0f}/{snapshot.sp_max}\n"
        f"    计算属性: 攻击力={attack_power:.1f} 防御力={defense_power:.1f} "
        f"攻速={attack_speed:.1f}"
    )


def format_warrior_current_stats(warrior: "Warrior") -> str:
    """格式化武将当前属性"""
    from src.constants import MAX_HP
    status = "阵亡" if not warrior.is_alive else "存活"
    return (
        f"  【{warrior.name}】[{status}]\n"
        f"    HP={warrior.hp:.0f}/{MAX_HP} ({warrior.hp_percent*100:.1f}%)\n"
        f"    SP={warrior.sp:.0f}/{warrior.sp_max} ({warrior.sp_percent*100:.1f}%)\n"
        f"    胆气={warrior.courage}"
    )


class BattleReporter:
    """战报生成器"""
    
    def __init__(self, team_a: List["Warrior"], team_b: List["Warrior"]):
        self.team_a = team_a
        self.team_b = team_b
        # 保存初始状态快照
        self.initial_snapshots_a = [take_snapshot(w) for w in team_a]
        self.initial_snapshots_b = [take_snapshot(w) for w in team_b]
    
    def generate_initial_report(self) -> str:
        """生成战斗前双方武将初始属性报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("【战斗开始 - 双方武将初始属性】")
        lines.append("=" * 70)
        
        lines.append("\n▶ A队阵容:")
        for snapshot in self.initial_snapshots_a:
            lines.append(format_warrior_initial_stats(snapshot))
        
        lines.append("\n▶ B队阵容:")
        for snapshot in self.initial_snapshots_b:
            lines.append(format_warrior_initial_stats(snapshot))
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def generate_round_report(self, logs: List["BattleLog"], round_num: int) -> str:
        """生成单个回合的战报"""
        round_logs = [log for log in logs if log.round_num == round_num]
        if not round_logs:
            return ""
        
        lines = []
        lines.append(f"\n{'─' * 70}")
        lines.append(f"【第 {round_num} 回合】")
        lines.append("─" * 70)
        
        for log in round_logs:
            if log.event_type == "attack":
                lines.append(self._format_attack_log(log))
            elif log.event_type == "clash":
                lines.append(self._format_clash_log(log))
            elif log.event_type == "round_end":
                pass  # 回合结束不需要额外输出
        
        return "\n".join(lines)
    
    def _format_attack_log(self, log: "BattleLog") -> str:
        """格式化攻击日志"""
        details = log.details
        attacker = details.get("attacker", "未知")
        defender = details.get("defender", "未知")
        defense = details.get("defense", "block")
        success = details.get("success", False)
        
        defense_cn = DEFENSE_TYPE_CN.get(defense, defense)
        success_text = "成功" if success else "失败"
        
        lines = []
        lines.append(f"\n  ⚔ {attacker} → {defender}")
        lines.append(f"    防御方式: {defense_cn}")
        lines.append(f"    判定结果: {success_text}")
        
        # 详细属性变化
        changes = []
        
        # 防守方HP变化
        target_hp_before = details.get("target_hp_before", 0)
        target_hp_after = details.get("target_hp_after", 0)
        if target_hp_before != target_hp_after:
            hp_diff = target_hp_before - target_hp_after
            changes.append(f"{defender} HP: {target_hp_before:.0f}→{target_hp_after:.0f} (-{hp_diff:.0f})")
        
        # 攻击方HP变化（反击/格挡反震）
        attacker_hp_before = details.get("attacker_hp_before", 0)
        attacker_hp_after = details.get("attacker_hp_after", 0)
        if attacker_hp_before != attacker_hp_after:
            hp_diff = attacker_hp_before - attacker_hp_after
            changes.append(f"{attacker} HP: {attacker_hp_before:.0f}→{attacker_hp_after:.0f} (-{hp_diff:.0f})")
        
        # 防守方SP变化
        target_sp_before = details.get("target_sp_before", 0)
        target_sp_after = details.get("target_sp_after", 0)
        if target_sp_before != target_sp_after:
            sp_diff = target_sp_before - target_sp_after
            changes.append(f"{defender} SP: {target_sp_before:.0f}→{target_sp_after:.0f} (-{sp_diff:.0f})")
        
        # 攻击方SP变化
        attacker_sp_before = details.get("attacker_sp_before", 0)
        attacker_sp_after = details.get("attacker_sp_after", 0)
        if attacker_sp_before != attacker_sp_after:
            sp_diff = attacker_sp_before - attacker_sp_after
            changes.append(f"{attacker} SP: {attacker_sp_before:.0f}→{attacker_sp_after:.0f} (-{sp_diff:.0f})")
        
        # 防守方胆气变化
        target_courage_before = details.get("target_courage_before", 0)
        target_courage_after = details.get("target_courage_after", 0)
        if target_courage_before != target_courage_after:
            courage_diff = target_courage_after - target_courage_before
            sign = "+" if courage_diff > 0 else ""
            changes.append(f"{defender} 胆气: {target_courage_before}→{target_courage_after} ({sign}{courage_diff})")
        
        if changes:
            lines.append(f"    属性变化:")
            for change in changes:
                lines.append(f"      • {change}")
        
        # 状态变化（阵亡）
        target_alive = details.get("target_alive", True)
        attacker_alive = details.get("attacker_alive", True)
        
        if not target_alive:
            lines.append(f"    ☠ {defender} 阵亡!")
        if not attacker_alive:
            lines.append(f"    ☠ {attacker} 阵亡!")
        
        return "\n".join(lines)
    
    def _format_clash_log(self, log: "BattleLog") -> str:
        """格式化拼刀日志"""
        details = log.details
        participants = details.get("participants", [])
        damages = details.get("damages", {})
        sp_costs = details.get("sp_costs", {})
        
        lines = []
        lines.append(f"\n  ⚔⚔ 拼刀! 参与者: {', '.join(participants)}")
        
        for name in participants:
            dmg = damages.get(name, 0)
            sp = sp_costs.get(name, 0)
            if dmg > 0 or sp > 0:
                lines.append(f"    {name}: HP-{dmg:.0f}, SP-{sp:.0f}")
        
        return "\n".join(lines)
    
    def generate_final_report(self, result: "BattleResult") -> str:
        """生成战斗结束后的最终报告"""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("【战斗结束 - 双方武将当前属性】")
        lines.append("=" * 70)
        
        # 战斗结果
        outcome_text = {
            "team_a_win": "A队胜利",
            "team_b_win": "B队胜利",
            "draw": "平局",
            "timeout": "超时判定"
        }
        lines.append(f"\n战斗结果: {outcome_text.get(result.outcome.value, result.outcome.value)}")
        lines.append(f"获胜方: {result.winner_team or '无'}")
        lines.append(f"总回合数: {result.rounds}")
        
        lines.append("\n▶ A队武将状态:")
        for warrior in self.team_a:
            lines.append(format_warrior_current_stats(warrior))
        
        lines.append("\n▶ B队武将状态:")
        for warrior in self.team_b:
            lines.append(format_warrior_current_stats(warrior))
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def _collect_defense_stats(self, logs: List["BattleLog"], total_rounds: int) -> Dict[str, WarriorDefenseStats]:
        """从战斗日志中收集防御统计数据"""
        stats: Dict[str, WarriorDefenseStats] = {}
        
        for log in logs:
            if log.event_type != "attack":
                continue
            
            details = log.details
            defender_name = details.get("defender", "")
            defense_type = details.get("defense", "block")
            success = details.get("success", False)
            
            # 从HP变化计算实际伤害（更准确）
            target_hp_before = details.get("target_hp_before", 0)
            target_hp_after = details.get("target_hp_after", 0)
            attacker_hp_before = details.get("attacker_hp_before", 0)
            attacker_hp_after = details.get("attacker_hp_after", 0)
            
            damage_to_defender = max(0, target_hp_before - target_hp_after)
            damage_to_attacker = max(0, attacker_hp_before - attacker_hp_after)
            
            # 初始化防守方统计
            if defender_name not in stats:
                stats[defender_name] = WarriorDefenseStats(
                    warrior_name=defender_name,
                    total_rounds=total_rounds
                )
            
            warrior_stats = stats[defender_name]
            warrior_stats.total_defenses += 1
            
            # 更新防御类型统计
            defense_stat = warrior_stats.defense_stats[defense_type]
            defense_stat.use_count += 1
            if success:
                defense_stat.success_count += 1
            defense_stat.total_damage_taken += damage_to_defender
            defense_stat.total_damage_dealt += damage_to_attacker
        
        return stats
    
    def _collect_total_damage_stats(self, logs: List["BattleLog"], total_rounds: int) -> Dict[str, float]:
        """收集每个武将受到的总伤害（包括防御时和攻击时受到的伤害）"""
        total_damage: Dict[str, float] = defaultdict(float)
        
        for log in logs:
            if log.event_type != "attack":
                continue
            
            details = log.details
            defender_name = details.get("defender", "")
            attacker_name = details.get("attacker", "")
            
            # 从HP变化计算实际伤害
            target_hp_before = details.get("target_hp_before", 0)
            target_hp_after = details.get("target_hp_after", 0)
            attacker_hp_before = details.get("attacker_hp_before", 0)
            attacker_hp_after = details.get("attacker_hp_after", 0)
            
            damage_to_defender = max(0, target_hp_before - target_hp_after)
            damage_to_attacker = max(0, attacker_hp_before - attacker_hp_after)
            
            if defender_name:
                total_damage[defender_name] += damage_to_defender
            if attacker_name:
                total_damage[attacker_name] += damage_to_attacker
        
        return dict(total_damage)
    
    def _collect_attack_stats(self, logs: List["BattleLog"], total_ticks: int) -> Dict[str, WarriorAttackStats]:
        """从战斗日志中收集攻击统计数据"""
        stats: Dict[str, WarriorAttackStats] = {}
        
        for log in logs:
            if log.event_type != "attack":
                continue
            
            attacker_name = log.details.get("attacker", "")
            tick = log.tick
            
            if attacker_name not in stats:
                stats[attacker_name] = WarriorAttackStats(
                    warrior_name=attacker_name,
                    total_ticks=total_ticks
                )
            
            stats[attacker_name].attack_count += 1
            stats[attacker_name].attack_ticks.append(tick)
        
        return stats
    
    def _collect_clash_stats(self, logs: List["BattleLog"]) -> ClashStats:
        """从战斗日志中收集拼刀统计数据"""
        stats = ClashStats()
        
        for log in logs:
            if log.event_type != "clash":
                continue
            
            details = log.details
            participants = details.get("participants", [])
            damages = details.get("damages", {})
            sp_costs = details.get("sp_costs", {})
            
            # 记录单次拼刀
            record = ClashRecord(
                round_num=log.round_num,
                tick=log.tick,
                participants=participants,
                damages=damages,
                sp_costs=sp_costs
            )
            stats.clash_records.append(record)
            stats.total_clashes += 1
            
            # 累计每个武将的拼刀伤害和体力消耗
            for name in participants:
                stats.warrior_clash_damage[name] += damages.get(name, 0)
                stats.warrior_clash_sp_cost[name] += sp_costs.get(name, 0)
                stats.warrior_clash_count[name] += 1
        
        return stats
    
    def _format_clash_stats(self, stats: ClashStats) -> str:
        """格式化拼刀统计报告"""
        if stats.total_clashes == 0:
            return ""
        
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("【拼刀统计】")
        lines.append("=" * 70)
        
        lines.append(f"\n总拼刀次数: {stats.total_clashes}")
        
        # 每次拼刀详情
        lines.append("\n▶ 拼刀详情:")
        for i, record in enumerate(stats.clash_records, 1):
            lines.append(f"\n  第{i}次拼刀 (回合{record.round_num}, tick={record.tick})")
            lines.append(f"    参与者: {', '.join(record.participants)}")
            for name in record.participants:
                dmg = record.damages.get(name, 0)
                sp = record.sp_costs.get(name, 0)
                lines.append(f"    {name}: HP-{dmg:.1f}, SP-{sp:.1f}")
        
        # 武将拼刀汇总
        lines.append("\n▶ 武将拼刀汇总:")
        lines.append(f"  {'武将':<10} {'参与次数':<10} {'总受伤':<12} {'总体力消耗':<12} {'平均受伤/次':<12}")
        lines.append(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*12}")
        
        for name in stats.warrior_clash_damage.keys():
            count = stats.warrior_clash_count[name]
            total_dmg = stats.warrior_clash_damage[name]
            total_sp = stats.warrior_clash_sp_cost[name]
            avg_dmg = total_dmg / count if count > 0 else 0
            lines.append(
                f"  {name:<10} {count:<10} {total_dmg:>10.1f}  {total_sp:>10.1f}  {avg_dmg:>10.1f}"
            )
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def _format_attack_stats(self, stats: Dict[str, WarriorAttackStats]) -> str:
        """格式化攻击统计报告"""
        if not stats:
            return ""
        
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("【攻击频率统计】")
        lines.append("=" * 70)
        
        lines.append(f"\n  {'武将':<10} {'攻击次数':<10} {'平均攻击间隔(tick)':<20}")
        lines.append(f"  {'-'*10} {'-'*10} {'-'*20}")
        
        for warrior_name, warrior_stats in stats.items():
            avg_interval = warrior_stats.avg_attack_interval
            lines.append(
                f"  {warrior_name:<10} {warrior_stats.attack_count:<10} {avg_interval:>10.1f}"
            )
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def _format_defense_stats(self, stats: Dict[str, WarriorDefenseStats], total_damage: Dict[str, float]) -> str:
        """格式化防御统计报告"""
        if not stats:
            return ""
        
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("【防御统计】")
        lines.append("=" * 70)
        
        for warrior_name, warrior_stats in stats.items():
            lines.append(f"\n▶ {warrior_name} 防御统计:")
            lines.append(f"  总防御次数: {warrior_stats.total_defenses}")
            lines.append("")
            
            # 表头 - "受伤害"是防御时受到的伤害，"造伤害"是对攻击方造成的伤害（反击/格挡反震）
            lines.append(f"  {'防御方式':<8} {'次数':<10} {'占比':<10} {'成功率':<10} {'防御受伤':<12} {'反伤敌方':<12} {'受伤/回合':<10}")
            lines.append(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
            
            total_defenses = warrior_stats.total_defenses
            total_rounds = warrior_stats.total_rounds or 1
            
            for defense_type in ALL_DEFENSE_TYPES:
                defense_stat = warrior_stats.defense_stats[defense_type]
                defense_cn = DEFENSE_TYPE_CN.get(defense_type, defense_type)
                
                use_count = defense_stat.use_count
                use_pct = (use_count / total_defenses * 100) if total_defenses > 0 else 0
                success_rate = (defense_stat.success_count / use_count * 100) if use_count > 0 else 0
                damage_taken = defense_stat.total_damage_taken
                damage_dealt = defense_stat.total_damage_dealt
                avg_damage_per_round = damage_taken / total_rounds
                
                lines.append(
                    f"  {defense_cn:<8} {use_count:<10} {use_pct:>6.1f}%   {success_rate:>6.1f}%   "
                    f"{damage_taken:>10.1f}  {damage_dealt:>10.1f}  {avg_damage_per_round:>8.1f}"
                )
            
            # 汇总行（仅防御时受伤）
            defense_damage_taken = sum(s.total_damage_taken for s in warrior_stats.defense_stats.values())
            total_damage_dealt = sum(s.total_damage_dealt for s in warrior_stats.defense_stats.values())
            defense_avg_damage = defense_damage_taken / total_rounds
            lines.append(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
            lines.append(
                f"  {'合计':<8} {total_defenses:<10} {'100.0%':<10} {'':<10} "
                f"{defense_damage_taken:>10.1f}  {total_damage_dealt:>10.1f}  {defense_avg_damage:>8.1f}"
            )
            
            # 显示总受伤（包括攻击时受到的反击/反震伤害）
            warrior_total_damage = total_damage.get(warrior_name, 0)
            attack_damage = warrior_total_damage - defense_damage_taken
            if attack_damage > 0:
                lines.append(f"\n  攻击时受伤(反击/反震): {attack_damage:.1f}")
            lines.append(f"  总受伤: {warrior_total_damage:.1f}  (受伤/回合: {warrior_total_damage/total_rounds:.1f})")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def generate_full_report(self, result: "BattleResult") -> str:
        """生成完整战报"""
        lines = []
        
        # 1. 初始属性
        lines.append(self.generate_initial_report())
        
        # 2. 按回合输出战报
        max_round = result.rounds
        for round_num in range(1, max_round + 1):
            round_report = self.generate_round_report(result.logs, round_num)
            if round_report:
                lines.append(round_report)
        
        # 3. 最终属性
        lines.append(self.generate_final_report(result))
        
        # 4. 攻击频率统计
        attack_stats = self._collect_attack_stats(result.logs, result.ticks)
        lines.append(self._format_attack_stats(attack_stats))
        
        # 5. 防御统计
        defense_stats = self._collect_defense_stats(result.logs, max_round)
        total_damage = self._collect_total_damage_stats(result.logs, max_round)
        lines.append(self._format_defense_stats(defense_stats, total_damage))
        
        # 6. 拼刀统计
        clash_stats = self._collect_clash_stats(result.logs)
        lines.append(self._format_clash_stats(clash_stats))
        
        return "\n".join(lines)


class AggregateReporter:
    """100次单挑总战报生成器"""
    
    def __init__(self, warrior_a_name: str, warrior_b_name: str):
        self.warrior_a_name = warrior_a_name
        self.warrior_b_name = warrior_b_name
        self.stats = AggregateStats()
        # 初始化防御统计
        for name in [warrior_a_name, warrior_b_name]:
            self.stats.defense_stats[name] = {
                dt: [0, 0] for dt in ALL_DEFENSE_TYPES  # [使用次数, 成功次数]
            }
            # 初始化防御伤害统计
            self.stats.defense_damage_stats[name] = {
                dt: [0.0, 0.0] for dt in ALL_DEFENSE_TYPES  # [受到伤害, 造成伤害]
            }
            # 初始化攻击伤害范围 [最高, 最低]
            self.stats.warrior_attack_damage_range[name] = [0.0, float('inf')]
    
    def add_battle_result(self, result: "BattleResult") -> None:
        """添加一场战斗结果到统计"""
        self.stats.total_battles += 1
        self.stats.total_rounds += result.rounds
        self.stats.total_ticks += result.ticks
        
        # 回合数统计
        if result.rounds < self.stats.min_rounds:
            self.stats.min_rounds = result.rounds
        if result.rounds > self.stats.max_rounds:
            self.stats.max_rounds = result.rounds
        
        # 胜负统计及胜负方HP/SP/胆气统计
        if result.winner_team == "A":
            self.stats.team_a_wins += 1
            for w in result.team_a_survivors:
                self.stats.team_a_winner_hp.append(w.hp)
                self.stats.team_a_winner_sp.append(w.sp)
                self.stats.team_a_winner_courage.append(w.courage)
            # 收集B队负方武将的SP和胆气（无论阵亡还是存活）
            for w in result.team_b:
                self.stats.team_b_loser_sp.append(w.sp)
                self.stats.team_b_loser_courage.append(w.courage)
        elif result.winner_team == "B":
            self.stats.team_b_wins += 1
            for w in result.team_b_survivors:
                self.stats.team_b_winner_hp.append(w.hp)
                self.stats.team_b_winner_sp.append(w.sp)
                self.stats.team_b_winner_courage.append(w.courage)
            # 收集A队负方武将的SP和胆气（无论阵亡还是存活）
            for w in result.team_a:
                self.stats.team_a_loser_sp.append(w.sp)
                self.stats.team_a_loser_courage.append(w.courage)
        else:
            self.stats.draws += 1
        
        # 统计同一武将在同一回合内攻击次数>1的回合数
        round_attacks = defaultdict(int)
        for log in result.logs:
            if log.event_type == "attack":
                attacker = log.details.get("attacker", "")
                round_attacks[(log.round_num, attacker)] += 1
        
        for (round_num, attacker), count in round_attacks.items():
            if count > 1:
                self.stats.multi_attack_rounds += 1
        
        # 从日志收集防御统计
        for log in result.logs:
            if log.event_type == "attack":
                details = log.details
                defender_name = details.get("defender", "")
                defense_type = details.get("defense", "block")
                success = details.get("success", False)
                attacker_name = details.get("attacker", "")
                
                if defender_name in self.stats.defense_stats:
                    self.stats.defense_stats[defender_name][defense_type][0] += 1
                    if success:
                        self.stats.defense_stats[defender_name][defense_type][1] += 1
                
                # 伤害统计
                target_hp_before = details.get("target_hp_before", 0)
                target_hp_after = details.get("target_hp_after", 0)
                attacker_hp_before = details.get("attacker_hp_before", 0)
                attacker_hp_after = details.get("attacker_hp_after", 0)
                
                damage_to_defender = max(0, target_hp_before - target_hp_after)
                damage_to_attacker = max(0, attacker_hp_before - attacker_hp_after)
                
                if defender_name:
                    self.stats.warrior_total_damage[defender_name] += damage_to_defender
                    # 防御伤害统计
                    if defender_name in self.stats.defense_damage_stats:
                        self.stats.defense_damage_stats[defender_name][defense_type][0] += damage_to_defender
                        self.stats.defense_damage_stats[defender_name][defense_type][1] += damage_to_attacker
                
                if attacker_name:
                    self.stats.warrior_total_damage[attacker_name] += damage_to_attacker
                    # 攻击时受到的伤害
                    self.stats.warrior_attack_damage_taken[attacker_name] += damage_to_attacker
                    
                    # 单次攻击伤害范围统计（攻击方造成的伤害，排除0）
                    if damage_to_defender > 0:
                        if attacker_name in self.stats.warrior_attack_damage_range:
                            if damage_to_defender > self.stats.warrior_attack_damage_range[attacker_name][0]:
                                self.stats.warrior_attack_damage_range[attacker_name][0] = damage_to_defender
                            if damage_to_defender < self.stats.warrior_attack_damage_range[attacker_name][1]:
                                self.stats.warrior_attack_damage_range[attacker_name][1] = damage_to_defender
            
            elif log.event_type == "clash":
                details = log.details
                participants = details.get("participants", [])
                damages = details.get("damages", {})
                sp_costs = details.get("sp_costs", {})
                
                self.stats.total_clashes += 1
                for name in participants:
                    self.stats.warrior_clash_count[name] += 1
                    self.stats.warrior_clash_damage[name] += damages.get(name, 0)
                    self.stats.warrior_clash_sp_cost[name] += sp_costs.get(name, 0)
    
    def generate_aggregate_report(self, snapshots_a: List[WarriorSnapshot], 
                                   snapshots_b: List[WarriorSnapshot]) -> str:
        """生成100次单挑的总战报"""
        lines = []
        s = self.stats
        
        # 标题
        lines.append("=" * 70)
        lines.append(f"【{s.total_battles}次单挑总战报】")
        lines.append("=" * 70)
        
        # 武将信息
        lines.append("\n▶ 对战双方:")
        for snapshot in snapshots_a:
            lines.append(format_warrior_initial_stats(snapshot))
        lines.append("  VS")
        for snapshot in snapshots_b:
            lines.append(format_warrior_initial_stats(snapshot))
        
        # 胜负统计
        lines.append("\n" + "=" * 70)
        lines.append("【胜负统计】")
        lines.append("=" * 70)
        
        total = s.total_battles
        a_rate = s.team_a_wins / total * 100 if total > 0 else 0
        b_rate = s.team_b_wins / total * 100 if total > 0 else 0
        draw_rate = s.draws / total * 100 if total > 0 else 0
        
        lines.append(f"\n  总场次: {total}")
        lines.append(f"  {self.warrior_a_name} 胜: {s.team_a_wins} ({a_rate:.1f}%)")
        lines.append(f"  {self.warrior_b_name} 胜: {s.team_b_wins} ({b_rate:.1f}%)")
        lines.append(f"  平局: {s.draws} ({draw_rate:.1f}%)")
        lines.append(f"\n  平均回合数: {s.total_rounds / total:.1f}")
        lines.append(f"  平均tick数: {s.total_ticks / total:.1f}")
        
        # 防御统计
        lines.append("\n" + "=" * 70)
        lines.append("【防御方式统计】")
        lines.append("=" * 70)
        
        for warrior_name in [self.warrior_a_name, self.warrior_b_name]:
            defense_data = s.defense_stats.get(warrior_name, {})
            total_uses = sum(d[0] for d in defense_data.values())
            
            lines.append(f"\n▶ {warrior_name} 防御统计 (总次数: {total_uses}):")
            lines.append(f"  {'防御方式':<8} {'使用次数':<10} {'占比':<10} {'成功次数':<10} {'成功率':<10}")
            lines.append(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
            
            for defense_type in ALL_DEFENSE_TYPES:
                data = defense_data.get(defense_type, [0, 0])
                use_count, success_count = data[0], data[1]
                use_pct = use_count / total_uses * 100 if total_uses > 0 else 0
                success_rate = success_count / use_count * 100 if use_count > 0 else 0
                defense_cn = DEFENSE_TYPE_CN.get(defense_type, defense_type)
                
                lines.append(
                    f"  {defense_cn:<8} {use_count:<10} {use_pct:>6.1f}%   {success_count:<10} {success_rate:>6.1f}%"
                )
        
        # 拼刀统计
        if s.total_clashes > 0:
            lines.append("\n" + "=" * 70)
            lines.append("【拼刀统计】")
            lines.append("=" * 70)
            
            avg_clashes = s.total_clashes / total
            lines.append(f"\n  总拼刀次数: {s.total_clashes}")
            lines.append(f"  平均每场拼刀: {avg_clashes:.2f}次")
            
            lines.append(f"\n  {'武将':<10} {'参与次数':<10} {'总受伤':<12} {'总体力消耗':<12} {'平均受伤/次':<12}")
            lines.append(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*12}")
            
            for name in [self.warrior_a_name, self.warrior_b_name]:
                count = s.warrior_clash_count.get(name, 0)
                total_dmg = s.warrior_clash_damage.get(name, 0)
                total_sp = s.warrior_clash_sp_cost.get(name, 0)
                avg_dmg = total_dmg / count if count > 0 else 0
                lines.append(
                    f"  {name:<10} {count:<10} {total_dmg:>10.1f}  {total_sp:>10.1f}  {avg_dmg:>10.1f}"
                )
        
        # 伤害统计
        lines.append("\n" + "=" * 70)
        lines.append("【伤害统计】")
        lines.append("=" * 70)
        
        lines.append(f"\n  {'武将':<10} {'总受伤':<12} {'平均受伤/场':<12}")
        lines.append(f"  {'-'*10} {'-'*12} {'-'*12}")
        
        for name in [self.warrior_a_name, self.warrior_b_name]:
            total_dmg = s.warrior_total_damage.get(name, 0)
            avg_dmg = total_dmg / total if total > 0 else 0
            lines.append(f"  {name:<10} {total_dmg:>10.1f}  {avg_dmg:>10.1f}")
        
        # 新增：每种防御方式的伤害统计
        lines.append("\n" + "=" * 70)
        lines.append("【防御方式伤害统计】")
        lines.append("=" * 70)
        
        for warrior_name in [self.warrior_a_name, self.warrior_b_name]:
            defense_dmg_data = s.defense_damage_stats.get(warrior_name, {})
            total_defense_damage_taken = sum(d[0] for d in defense_dmg_data.values())
            total_defense_damage_dealt = sum(d[1] for d in defense_dmg_data.values())
            
            lines.append(f"\n▶ {warrior_name} 防御伤害统计:")
            lines.append(f"  {'防御方式':<8} {'受到伤害':<12} {'受伤占比':<10} {'造成伤害':<12} {'造伤占比':<10}")
            lines.append(f"  {'-'*8} {'-'*12} {'-'*10} {'-'*12} {'-'*10}")
            
            for defense_type in ALL_DEFENSE_TYPES:
                data = defense_dmg_data.get(defense_type, [0.0, 0.0])
                damage_taken, damage_dealt = data[0], data[1]
                taken_pct = damage_taken / total_defense_damage_taken * 100 if total_defense_damage_taken > 0 else 0
                dealt_pct = damage_dealt / total_defense_damage_dealt * 100 if total_defense_damage_dealt > 0 else 0
                defense_cn = DEFENSE_TYPE_CN.get(defense_type, defense_type)
                
                lines.append(
                    f"  {defense_cn:<8} {damage_taken:>10.1f}  {taken_pct:>6.1f}%   {damage_dealt:>10.1f}  {dealt_pct:>6.1f}%"
                )
            
            lines.append(f"  {'-'*8} {'-'*12} {'-'*10} {'-'*12} {'-'*10}")
            lines.append(
                f"  {'合计':<8} {total_defense_damage_taken:>10.1f}  {'100.0%':<10} {total_defense_damage_dealt:>10.1f}  {'100.0%':<10}"
            )
        
        # 新增：攻击受伤与防御受伤比例
        lines.append("\n" + "=" * 70)
        lines.append("【攻击/防御受伤比例】")
        lines.append("=" * 70)
        
        lines.append(f"\n  {'武将':<10} {'攻击时受伤':<12} {'防御时受伤':<12} {'攻击受伤占比':<12} {'防御受伤占比':<12}")
        lines.append(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
        
        for name in [self.warrior_a_name, self.warrior_b_name]:
            attack_dmg_taken = s.warrior_attack_damage_taken.get(name, 0)
            defense_dmg_data = s.defense_damage_stats.get(name, {})
            defense_dmg_taken = sum(d[0] for d in defense_dmg_data.values())
            total_dmg = attack_dmg_taken + defense_dmg_taken
            attack_pct = attack_dmg_taken / total_dmg * 100 if total_dmg > 0 else 0
            defense_pct = defense_dmg_taken / total_dmg * 100 if total_dmg > 0 else 0
            lines.append(
                f"  {name:<10} {attack_dmg_taken:>10.1f}  {defense_dmg_taken:>10.1f}  {attack_pct:>8.1f}%     {defense_pct:>8.1f}%"
            )
        
        # 新增：单次攻击伤害范围
        lines.append("\n" + "=" * 70)
        lines.append("【单次攻击伤害范围（不含拼刀、排除0）】")
        lines.append("=" * 70)
        
        lines.append(f"\n  {'武将':<10} {'最高伤害':<12} {'最低伤害':<12}")
        lines.append(f"  {'-'*10} {'-'*12} {'-'*12}")
        
        for name in [self.warrior_a_name, self.warrior_b_name]:
            dmg_range = s.warrior_attack_damage_range.get(name, [0.0, float('inf')])
            max_dmg = dmg_range[0]
            min_dmg = dmg_range[1] if dmg_range[1] != float('inf') else 0.0
            lines.append(f"  {name:<10} {max_dmg:>10.1f}  {min_dmg:>10.1f}")
        
        # 新增：回合数统计
        lines.append("\n" + "=" * 70)
        lines.append("【回合数统计】")
        lines.append("=" * 70)
        
        avg_rounds = s.total_rounds / total if total > 0 else 0
        min_rounds = s.min_rounds if s.min_rounds != 999999 else 0
        lines.append(f"\n  最多回合数: {s.max_rounds}")
        lines.append(f"  最少回合数: {min_rounds}")
        lines.append(f"  平均回合数: {avg_rounds:.1f}")
        
        # 新增：胜负方HP/SP/胆气统计 - 按队伍分别统计
        lines.append("\n" + "=" * 70)
        lines.append("【胜负方HP/SP/胆气剩余统计】")
        lines.append("=" * 70)
        
        lines.append(f"\n▶ {self.warrior_a_name}(A队) 获胜时剩余:")
        if s.team_a_winner_hp:
            max_hp = max(s.team_a_winner_hp)
            min_hp = min(s.team_a_winner_hp)
            avg_hp = sum(s.team_a_winner_hp) / len(s.team_a_winner_hp)
            lines.append(f"  HP: 最高={max_hp:.1f}, 最低={min_hp:.1f}, 平均={avg_hp:.1f}")
            
            max_sp = max(s.team_a_winner_sp)
            min_sp = min(s.team_a_winner_sp)
            avg_sp = sum(s.team_a_winner_sp) / len(s.team_a_winner_sp)
            lines.append(f"  SP: 最高={max_sp:.1f}, 最低={min_sp:.1f}, 平均={avg_sp:.1f}")
            
            max_courage = max(s.team_a_winner_courage)
            min_courage = min(s.team_a_winner_courage)
            avg_courage = sum(s.team_a_winner_courage) / len(s.team_a_winner_courage)
            lines.append(f"  胆气: 最高={max_courage}, 最低={min_courage}, 平均={avg_courage:.1f}")
        else:
            lines.append("  无数据（未获胜）")
        
        lines.append(f"\n▶ {self.warrior_a_name}(A队) 阵亡时剩余:")
        if s.team_a_loser_sp:
            max_sp = max(s.team_a_loser_sp)
            min_sp = min(s.team_a_loser_sp)
            avg_sp = sum(s.team_a_loser_sp) / len(s.team_a_loser_sp)
            lines.append(f"  SP: 最高={max_sp:.1f}, 最低={min_sp:.1f}, 平均={avg_sp:.1f}")
            
            max_courage = max(s.team_a_loser_courage)
            min_courage = min(s.team_a_loser_courage)
            avg_courage = sum(s.team_a_loser_courage) / len(s.team_a_loser_courage)
            lines.append(f"  胆气: 最高={max_courage}, 最低={min_courage}, 平均={avg_courage:.1f}")
        else:
            lines.append("  无数据（未阵亡）")
        
        lines.append(f"\n▶ {self.warrior_b_name}(B队) 获胜时剩余:")
        if s.team_b_winner_hp:
            max_hp = max(s.team_b_winner_hp)
            min_hp = min(s.team_b_winner_hp)
            avg_hp = sum(s.team_b_winner_hp) / len(s.team_b_winner_hp)
            lines.append(f"  HP: 最高={max_hp:.1f}, 最低={min_hp:.1f}, 平均={avg_hp:.1f}")
            
            max_sp = max(s.team_b_winner_sp)
            min_sp = min(s.team_b_winner_sp)
            avg_sp = sum(s.team_b_winner_sp) / len(s.team_b_winner_sp)
            lines.append(f"  SP: 最高={max_sp:.1f}, 最低={min_sp:.1f}, 平均={avg_sp:.1f}")
            
            max_courage = max(s.team_b_winner_courage)
            min_courage = min(s.team_b_winner_courage)
            avg_courage = sum(s.team_b_winner_courage) / len(s.team_b_winner_courage)
            lines.append(f"  胆气: 最高={max_courage}, 最低={min_courage}, 平均={avg_courage:.1f}")
        else:
            lines.append("  无数据（未获胜）")
        
        lines.append(f"\n▶ {self.warrior_b_name}(B队) 阵亡时剩余:")
        if s.team_b_loser_sp:
            max_sp = max(s.team_b_loser_sp)
            min_sp = min(s.team_b_loser_sp)
            avg_sp = sum(s.team_b_loser_sp) / len(s.team_b_loser_sp)
            lines.append(f"  SP: 最高={max_sp:.1f}, 最低={min_sp:.1f}, 平均={avg_sp:.1f}")
            
            max_courage = max(s.team_b_loser_courage)
            min_courage = min(s.team_b_loser_courage)
            avg_courage = sum(s.team_b_loser_courage) / len(s.team_b_loser_courage)
            lines.append(f"  胆气: 最高={max_courage}, 最低={min_courage}, 平均={avg_courage:.1f}")
        else:
            lines.append("  无数据（未阵亡）")
        
        # 新增：回合内多次攻击统计
        lines.append("\n" + "=" * 70)
        lines.append("【回合内同一武将多次攻击统计】")
        lines.append("=" * 70)
        
        lines.append(f"\n  同一武将攻击次数>1的回合数: {s.multi_attack_rounds}")
        lines.append(f"  总回合数: {s.total_rounds}")
        multi_attack_rate = s.multi_attack_rounds / s.total_rounds * 100 if s.total_rounds > 0 else 0
        lines.append(f"  占比: {multi_attack_rate:.1f}%")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
