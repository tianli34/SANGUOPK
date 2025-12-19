from enum import Enum


class DefenseType(Enum):
    """武将可用的防御类型"""
    BLOCK = "block"      # 格挡(硬接)
    PARRY = "parry"       # 卸力
    DODGE = "dodge"       # 闪避
    COUNTER = "counter"   # 反击
