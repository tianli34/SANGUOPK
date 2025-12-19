"""武将对决系统的武将类"""
import random
from typing import Optional
from src.constants import MAX_HP, AP_LIMIT, COURAGE_CAP, SP_EXPANSION_FACTOR
from src.enums import DefenseType


class Warrior:
    """武将对决系统中的武将"""
    
    def __init__(
        self,
        name: str,
        team: str,
        martial_arts: int = 50,
        agility: int = 50,
        strength: int = 50,
        courage: int = 50,
        sp: int = 50
    ):
        self.name = name
        self.team = team
        
        # 基础属性(四维属性)
        self.martial_arts = martial_arts  # 武艺
        self.agility = agility            # 敏捷
        self.strength = strength          # 力量
        self.courage = courage            # 胆气
        
        # 运行时状态
        self.hp = MAX_HP                    # 生命值
        self.sp_max = sp * SP_EXPANSION_FACTOR  # 体力上限
        self.sp = sp * SP_EXPANSION_FACTOR      # 当前体力
        self.ap = 0.0                       # 行动点数
        self.is_alive = True                # 存活状态
    
    @property
    def attack_speed(self) -> float:
        """根据敏捷和体力比例计算攻击速度"""
        sp_ratio = min(1.0, (self.sp / self.sp_max) / 0.5)
        return (100 + self.agility * 2) * sp_ratio
    
    @property
    def attack_power(self) -> float:
        """计算攻击力: 力量×1.5 + 武艺×0.5"""
        return self.strength * 1.5 + self.martial_arts * 0.5
    
    @property
    def defense_power(self) -> float:
        """计算防御力: 力量×0.5 + 体力上限×0.01"""
        return self.strength * 0.5 + self.sp_max * 0.01

    @property
    def base_impact(self) -> float:
        """计算基础冲击力: 力量×0.1"""
        return self.strength * 0.1
    
    @property
    def sp_percent(self) -> float:
        """当前体力百分比"""
        return self.sp / self.sp_max
    
    @property
    def sp_raw(self) -> float:
        """当前体力原始值（未膨胀）"""
        return self.sp / SP_EXPANSION_FACTOR
    
    @property
    def hp_percent(self) -> float:
        """当前生命值百分比"""
        return self.hp / MAX_HP
    
    @property
    def ap_percent(self) -> float:
        """当前行动点数百分比"""
        return self.ap / AP_LIMIT
    
    def tick_ap(self, tick_rate: float) -> None:
        """根据攻击速度累积行动点数"""
        if self.is_alive:
            self.ap += self.attack_speed * tick_rate
    
    def can_attack(self) -> bool:
        """检查是否达到行动点数阈值"""
        return self.is_alive and self.ap >= AP_LIMIT
    
    def reset_ap(self) -> None:
        """攻击后重置行动点数"""
        self.ap = 0.0
    
    def take_damage(self, damage: float) -> None:
        """对武将造成伤害"""
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            self.is_alive = False
    
    def consume_sp(self, amount: float) -> None:
        """消耗体力"""
        self.sp = max(0, self.sp - amount)
    
    def modify_courage(self, amount: int) -> None:
        """在限制范围内修改胆气"""
        self.courage = max(0, min(COURAGE_CAP, self.courage + amount))
    
    def choose_defense(self) -> DefenseType:
        """AI根据加权属性选择防御类型"""
        # counter_weight = (self.courage * 0.7 + self.martial_arts * 0.3) * (1 - self.hp_percent) 
        
        weights = {
            DefenseType.BLOCK: self.strength * 0.6 + self.sp_percent * 100 * 0.4,
            DefenseType.PARRY: self.martial_arts * 0.7 + self.agility * 0.3,
            DefenseType.DODGE: self.agility * 0.8 + (COURAGE_CAP - self.courage) * 0.2,
            DefenseType.COUNTER: (self.courage * 0.7 + self.martial_arts * 0.3) * (1 - self.hp_percent) ,
        }
        
        total = sum(weights.values())
        roll = random.uniform(0, total)
        cumulative = 0.0
        
        for defense_type, weight in weights.items():
            cumulative += weight
            if roll <= cumulative:
                return defense_type
        
        return DefenseType.BLOCK
    
    def __repr__(self) -> str:
        return f"Warrior({self.name}, HP={self.hp:.0f}, SP={self.sp:.0f}, AP={self.ap:.0f})"
