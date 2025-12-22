# 文件名: battle_engine.py
# 用途: 战斗引擎核心模块，负责管理战斗流程、回合控制、攻击判定和战斗结果输出
"""武将对决系统的战斗引擎"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

from src.constants import TICK_RATE, MAX_ROUNDS, MAX_TICKS
from src.warrior import Warrior
from src.defense import process_defense
from src.damage import calculate_final_damage
from src.clash import check_clash_condition, process_clash


class BattleOutcome(Enum):
    """可能的战斗结果"""

    TEAM_A_WIN = "team_a_win"  # A队胜利
    TEAM_B_WIN = "team_b_win"  # B队胜利
    DRAW = "draw"  # 平局
    TIMEOUT = "timeout"  # 超时


@dataclass
class BattleLog:
    """战斗事件日志条目"""

    tick: int  # 时间刻度
    round_num: int  # 回合数
    event_type: str  # 事件类型
    description: str  # 事件描述
    details: dict = field(default_factory=dict)  # 详细信息


@dataclass
class BattleResult:
    """战斗最终结果"""

    outcome: BattleOutcome  # 战斗结果
    winner_team: Optional[str]  # 获胜队伍
    rounds: int  # 总回合数
    ticks: int  # 总时间刻度数
    team_a_survivors: List[Warrior]  # A队幸存者
    team_b_survivors: List[Warrior]  # B队幸存者
    logs: List[BattleLog]  # 战斗日志
    team_a: List[Warrior] = field(default_factory=list)  # A队所有武将
    team_b: List[Warrior] = field(default_factory=list)  # B队所有武将


class BattleEngine:
    """运行武将对决模拟的主要战斗引擎"""

    def __init__(self, team_a: List[Warrior], team_b: List[Warrior]):
        self.team_a = team_a
        self.team_b = team_b
        self.all_warriors = team_a + team_b

        self.tick_count = 0  # 时间刻度计数器
        self.round_count = 0  # 回合计数器
        self.attack_count = 0  # 攻击次数计数器
        self.logs: List[BattleLog] = []  # 战斗日志
        self.last_attack_tick = {}  # 记录每个武将上次攻击的tick

        self._validate_teams()

    def _validate_teams(self) -> None:
        """确保队伍正确设置"""
        for w in self.team_a:
            w.team = "A"
        for w in self.team_b:
            w.team = "B"

    def _log(self, event_type: str, description: str, **details) -> None:
        """添加日志条目"""
        self.logs.append(
            BattleLog(
                tick=self.tick_count,
                round_num=self.round_count,
                event_type=event_type,
                description=description,
                details=details,
            )
        )

    def _get_alive(self, team: str) -> List[Warrior]:
        """获取指定队伍存活的武将"""
        warriors = self.team_a if team == "A" else self.team_b
        return [w for w in warriors if w.is_alive]

    def _get_all_alive(self) -> List[Warrior]:
        """获取所有存活的武将"""
        return [w for w in self.all_warriors if w.is_alive]

    def _find_target(self, attacker: Warrior) -> Optional[Warrior]:
        """寻找目标：生命值最低的敌人"""
        enemy_team = "B" if attacker.team == "A" else "A"
        enemies = self._get_alive(enemy_team)
        if not enemies:
            return None
        return min(enemies, key=lambda w: w.hp)

    def _check_battle_end(self) -> Optional[BattleResult]:
        """检查战斗是否应该结束"""
        alive_a = self._get_alive("A")
        alive_b = self._get_alive("B")

        # 双方全灭 - 平局
        if not alive_a and not alive_b:
            self._log("battle_end", "双方同归于尽！平局！")
            return BattleResult(
                outcome=BattleOutcome.DRAW,
                winner_team=None,
                rounds=self.round_count,
                ticks=self.tick_count,
                team_a_survivors=[],
                team_b_survivors=[],
                logs=self.logs,
                team_a=self.team_a,
                team_b=self.team_b,
            )

        # A队全灭
        if not alive_a:
            self._log("battle_end", "A队全灭，B队获胜！")
            return BattleResult(
                outcome=BattleOutcome.TEAM_B_WIN,
                winner_team="B",
                rounds=self.round_count,
                ticks=self.tick_count,
                team_a_survivors=[],
                team_b_survivors=alive_b,
                logs=self.logs,
                team_a=self.team_a,
                team_b=self.team_b,
            )

        # B队全灭
        if not alive_b:
            self._log("battle_end", "B队全灭，A队获胜！")
            return BattleResult(
                outcome=BattleOutcome.TEAM_A_WIN,
                winner_team="A",
                rounds=self.round_count,
                ticks=self.tick_count,
                team_a_survivors=alive_a,
                team_b_survivors=[],
                logs=self.logs,
                team_a=self.team_a,
                team_b=self.team_b,
            )

        return None

    def _check_timeout(self) -> Optional[BattleResult]:
        """检查超时并根据生命值百分比决定胜者"""
        # 优先检查时间刻度超时（防止无限循环）
        if self.tick_count < MAX_TICKS and self.round_count < MAX_ROUNDS:
            return None

        alive_a = self._get_alive("A")
        alive_b = self._get_alive("B")

        # 计算生命值百分比
        total_max_a = sum(w.hp_real for w in self.team_a)
        total_max_b = sum(w.hp_real for w in self.team_b)

        current_hp_a = sum(w.hp for w in alive_a)
        current_hp_b = sum(w.hp for w in alive_b)

        pct_a = current_hp_a / total_max_a if total_max_a > 0 else 0
        pct_b = current_hp_b / total_max_b if total_max_b > 0 else 0

        self._log("timeout", f"达到最大回合数！A队血量{pct_a:.1%}，B队血量{pct_b:.1%}")

        if pct_a > pct_b:
            return BattleResult(
                outcome=BattleOutcome.TIMEOUT,
                winner_team="A",
                rounds=self.round_count,
                ticks=self.tick_count,
                team_a_survivors=alive_a,
                team_b_survivors=alive_b,
                logs=self.logs,
                team_a=self.team_a,
                team_b=self.team_b,
            )
        elif pct_b > pct_a:
            return BattleResult(
                outcome=BattleOutcome.TIMEOUT,
                winner_team="B",
                rounds=self.round_count,
                ticks=self.tick_count,
                team_a_survivors=alive_a,
                team_b_survivors=alive_b,
                logs=self.logs,
                team_a=self.team_a,
                team_b=self.team_b,
            )
        else:
            return BattleResult(
                outcome=BattleOutcome.DRAW,
                winner_team=None,
                rounds=self.round_count,
                ticks=self.tick_count,
                team_a_survivors=alive_a,
                team_b_survivors=alive_b,
                logs=self.logs,
                team_a=self.team_a,
                team_b=self.team_b,
            )

    def _process_single_attack(self, attacker: Warrior) -> None:
        """处理单个攻击动作"""
        target = self._find_target(attacker)
        if not target:
            attacker.reset_ap()
            return

        # 记录攻击前状态
        attacker_hp_before = attacker.hp
        attacker_sp_before = attacker.sp
        target_hp_before = target.hp
        target_sp_before = target.sp
        target_courage_before = target.courage
        target_ap_percent = target.ap_percent  # 记录防守方AP百分比

        # 防守方选择防御方式
        defense_type = target.choose_defense()
        base_damage = calculate_final_damage(attacker, target)

        # 计算防御成功率
        from src.defense import calculate_defense_rate
        defense_rate = calculate_defense_rate(defense_type, target, attacker)

        # 处理防御
        result = process_defense(defense_type, target, attacker, base_damage)

        # 应用结果
        if result.damage_to_defender > 0:
            target.take_damage(result.damage_to_defender)
        if result.damage_to_attacker > 0:
            attacker.take_damage(result.damage_to_attacker)

        target.consume_sp(result.defender_sp_cost)
        attacker.consume_sp(result.attacker_sp_cost + 10)  # 每次攻击额外消耗10点SP
        target.modify_courage(result.defender_courage_change)

        # 计算攻击间隔（第一次攻击间隔为从战斗开始到现在）
        attack_interval_ticks = self.tick_count - self.last_attack_tick.get(attacker.name, 0)
        self.last_attack_tick[attacker.name] = self.tick_count

        # 记录攻击日志（包含详细状态变化）
        self._log(
            "attack",
            f"{attacker.name} 攻击 {target.name}，{target.name} 选择 {defense_type.value}",
            attacker=attacker.name,
            defender=target.name,
            defense=defense_type.value,
            success=result.success,
            defense_rate=defense_rate,  # 记录防御成功率
            defender_ap_percent=target_ap_percent,  # 记录防守方AP百分比
            attack_interval_ticks=attack_interval_ticks,  # 记录攻击间隔
            damage_to_defender=result.damage_to_defender,
            damage_to_attacker=result.damage_to_attacker,
            defender_sp_cost=result.defender_sp_cost,
            attacker_sp_cost=result.attacker_sp_cost + 10,  # 包含额外的10点SP消耗
            defender_courage_change=result.defender_courage_change,
            # 状态变化记录
            attacker_hp_before=attacker_hp_before,
            attacker_hp_after=attacker.hp,
            attacker_sp_before=attacker_sp_before,
            attacker_sp_after=attacker.sp,
            target_hp_before=target_hp_before,
            target_hp_after=target.hp,
            target_sp_before=target_sp_before,
            target_sp_after=target.sp,
            target_courage_before=target_courage_before,
            target_courage_after=target.courage,
            target_alive=target.is_alive,
            attacker_alive=attacker.is_alive,
        )

        attacker.reset_ap()
        self.attack_count += 1

    def _process_clash(self, ready_warriors: List[Warrior]) -> None:
        """处理多个武将之间的拼刀"""
        clash_result = process_clash(ready_warriors)

        # 应用伤害和体力消耗
        for warrior in ready_warriors:
            damage = clash_result.damages[warrior.name]
            sp_cost = clash_result.sp_costs[warrior.name]
            warrior.take_damage(damage)
            warrior.consume_sp(sp_cost)
            warrior.reset_ap()

        self._log(
            "clash",
            f"拼刀！参与者: {', '.join(w.name for w in ready_warriors)}",
            participants=[w.name for w in ready_warriors],
            damages=clash_result.damages,
            sp_costs=clash_result.sp_costs,
        )

        self.attack_count += len(ready_warriors)

    def _check_round_end(self) -> None:
        """检查回合是否应该结束"""
        alive_count = len(self._get_all_alive())
        if alive_count > 0 and self.attack_count >= alive_count:
            self.round_count += 1
            self.attack_count = 0
            self._log("round_end", f"第 {self.round_count} 回合结束")

    def run_tick(self) -> Optional[BattleResult]:
        """运行战斗的一个时间刻度"""
        self.tick_count += 1

        # 为所有存活武将累积行动点数
        for warrior in self._get_all_alive():
            warrior.tick_ap(TICK_RATE)

        # 获取准备攻击的武将
        ready = [w for w in self._get_all_alive() if w.can_attack()]

        if len(ready) >= 2 and check_clash_condition(ready):
            # 拼刀！
            self._process_clash(ready)
        elif ready:
            # 按顺序进行单个攻击
            for attacker in ready:
                if attacker.is_alive:
                    self._process_single_attack(attacker)

        # 检查战斗是否结束（在所有伤害应用后）
        result = self._check_battle_end()
        if result:
            return result

        # 检查回合是否结束
        self._check_round_end()

        # 检查是否超时
        return self._check_timeout()

    def run(self) -> BattleResult:
        """运行完整战斗直到结束"""
        self._log("battle_start", "战斗开始！")
        self.round_count = 1

        while True:
            result = self.run_tick()
            if result:
                return result
