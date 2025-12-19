# Design Document: Warrior Duel System

## Overview

武将对决系统是一个基于行动点(AP)的回合制自动战斗模拟器。系统采用Python实现，使用面向对象设计，将武将、战斗引擎、防御系统、伤害计算等模块化。战斗过程完全自动化，AI根据武将属性选择最优防御策略。

核心特性：
- 基于Tick的时间推进系统（每Tick 0.05秒）
- AP累积触发攻击机制
- 四种防御策略（硬接、卸力、闪避、反击）的AI选择
- 拼刀系统处理同时攻击
- 完整的胜负判定逻辑

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      BattleEngine                           │
│  - 管理战斗主循环                                            │
│  - 协调各子系统                                              │
│  - 处理回合和Tick                                            │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Warrior   │ │DefenseSystem│ │DamageSystem │ │ ClashSystem │
│  - 属性管理  │ │ - 权重计算   │ │ - 伤害公式   │ │ - 拼刀判定   │
│  - 状态更新  │ │ - 成功率    │ │ - 倍率计算   │ │ - 拼刀伤害   │
│  - 攻速计算  │ │ - 结果处理   │ │ - 最终伤害   │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 模块职责

| 模块 | 职责 |
|------|------|
| Warrior | 武将实体，管理属性和状态 |
| BattleEngine | 战斗主控制器，管理Tick循环和回合 |
| DefenseSystem | 防御选择和判定逻辑 |
| DamageSystem | 伤害计算逻辑 |
| ClashSystem | 拼刀触发和处理 |
| BattleResult | 战斗结果和胜负判定 |

## Components and Interfaces

### Warrior Class

```python
@dataclass
class Warrior:
    # 基础信息
    name: str
    team: str  # "A" or "B"
    
    # 五维属性
    martial_arts: int   # 武艺
    agility: int        # 敏捷
    strength: int       # 力量
    courage: int        # 胆气
    stamina_max: int    # 耐力上限
    
    # 实时状态
    hp: int = MAX_HP
    sp: int = MAX_SP
    ap: float = 0.0
    is_alive: bool = True
    
    def get_attack_speed(self) -> float
    def take_damage(self, damage: int) -> None
    def consume_sp(self, amount: int) -> None
    def modify_courage(self, delta: int) -> None
    def reset_ap(self) -> None
```

### BattleEngine Class

```python
class BattleEngine:
    def __init__(self, team_a: List[Warrior], team_b: List[Warrior])
    def run_battle(self) -> BattleResult
    def run_tick(self) -> Optional[BattleResult]
    def get_ready_warriors(self) -> List[Warrior]
    def select_target(self, attacker: Warrior) -> Optional[Warrior]
    def check_battle_end(self) -> Optional[BattleResult]
```

### DefenseSystem Class

```python
class DefenseSystem:
    @staticmethod
    def select_defense(defender: Warrior, attacker: Warrior) -> DefenseType
    
    @staticmethod
    def calculate_block_weight(defender: Warrior) -> float
    
    @staticmethod
    def calculate_parry_weight(defender: Warrior) -> float
    
    @staticmethod
    def calculate_dodge_weight(defender: Warrior) -> float
    
    @staticmethod
    def calculate_counter_weight(defender: Warrior) -> float
    
    @staticmethod
    def calculate_parry_success_rate(defender: Warrior, attacker: Warrior) -> float
    
    @staticmethod
    def calculate_dodge_success_rate(defender: Warrior, attacker: Warrior) -> float
    
    @staticmethod
    def calculate_counter_success_rate(defender: Warrior, attacker: Warrior) -> float
    
    @staticmethod
    def apply_defense_result(defender: Warrior, attacker: Warrior, 
                             defense_type: DefenseType, success: bool) -> DefenseResult
```

### DamageSystem Class

```python
class DamageSystem:
    @staticmethod
    def calculate_attack_power(warrior: Warrior) -> float
    
    @staticmethod
    def calculate_defense_power(warrior: Warrior) -> float
    
    @staticmethod
    def calculate_base_damage(attacker: Warrior, defender: Warrior) -> float
    
    @staticmethod
    def calculate_final_damage(attacker: Warrior, defender: Warrior, 
                               multiplier: float = 1.0) -> int
    
    @staticmethod
    def calculate_block_damage(attacker: Warrior, defender: Warrior) -> Tuple[int, int]
```

### ClashSystem Class

```python
class ClashSystem:
    @staticmethod
    def check_clash(ready_warriors: List[Warrior]) -> Optional[Tuple[Warrior, Warrior]]
    
    @staticmethod
    def execute_clash(warrior_a: Warrior, warrior_b: Warrior) -> ClashResult
    
    @staticmethod
    def calculate_clash_damage(attacker: Warrior, defender: Warrior) -> int
```

### Enums and Data Classes

```python
class DefenseType(Enum):
    BLOCK = "block"
    PARRY = "parry"
    DODGE = "dodge"
    COUNTER = "counter"

@dataclass
class DefenseResult:
    defense_type: DefenseType
    success: bool
    damage_to_defender: int
    damage_to_attacker: int
    sp_cost_defender: int
    sp_cost_attacker: int
    courage_change: int

@dataclass
class ClashResult:
    damage_to_a: int
    damage_to_b: int
    sp_cost_a: int
    sp_cost_b: int

@dataclass
class BattleResult:
    winner: Optional[str]  # "A", "B", or None for draw
    reason: str  # "elimination", "draw", "timeout"
    rounds: int
    final_state: Dict
```

## Data Models

### 全局常量

```python
MAX_HP = 10000
MAX_SP = 5000
AP_LIMIT = 500
TICK_RATE = 0.05
CLASH_AP_THRESHOLD = 20
BLOCK_K = 0.5
BASE_SP_COST = 5
COURAGE_CAP = 120
RECOIL_CAP_RATIO = 0.5
MAX_ROUNDS = 100
ARMOR_PENETRATION = 1.0  # 默认破甲系数
```

### 防御参数

```python
DEFENSE_PARAMS = {
    "parry": {
        "base_rate": 0.40,
        "rate_factor": 0.015,
        "success_sp_cost": 5,
        "success_courage": 20,
        "fail_sp_cost": 20,
        "fail_courage": -20,
        "fail_damage_mult": 1.0
    },
    "dodge": {
        "base_rate": 0.50,
        "rate_factor": 0.01,
        "success_sp_cost": 12,
        "success_courage": 30,
        "fail_sp_cost": 25,
        "fail_courage": -30,
        "fail_damage_mult": 1.2
    },
    "counter": {
        "base_rate": 0.30,
        "rate_factor": 0.01,
        "success_sp_cost": 20,
        "success_courage": 40,
        "fail_sp_cost": 20,
        "fail_courage": -40,
        "fail_damage_mult": 1.5
    }
}
```

### 战斗状态序列化格式

```json
{
  "round": 1,
  "tick": 50,
  "team_a": [
    {
      "name": "关羽",
      "martial_arts": 95,
      "agility": 80,
      "strength": 98,
      "courage": 100,
      "stamina_max": 90,
      "hp": 8500,
      "sp": 4200,
      "ap": 250.5,
      "is_alive": true
    }
  ],
  "team_b": [...]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Warrior Initialization Invariants
*For any* warrior created with valid attributes, the warrior SHALL have HP equal to MAX_HP (10000), SP equal to MAX_SP (5000), AP equal to 0, and is_alive equal to true.
**Validates: Requirements 1.2**

### Property 2: Attack Speed Formula Correctness
*For any* warrior with agility in range [1, 100] and SP in range [0, MAX_SP], the calculated attack speed SHALL equal (100 + agility × 2) × min(1, (current_SP / MAX_SP) / 0.5).
**Validates: Requirements 1.3**

### Property 3: Death State Transition
*For any* warrior, when HP is reduced to zero or below, is_alive SHALL become false.
**Validates: Requirements 1.4**

### Property 4: AP Accumulation Per Tick
*For any* alive warrior, after one tick, the warrior's AP SHALL increase by exactly attack_speed × TICK_RATE (0.05).
**Validates: Requirements 2.1**

### Property 5: AP Reset After Attack
*For any* warrior that completes an attack, the warrior's AP SHALL be reset to zero.
**Validates: Requirements 2.3**

### Property 6: Target Selection - Lowest HP Priority
*For any* set of alive enemy warriors, the selected target SHALL be the warrior with the lowest current HP.
**Validates: Requirements 2.4**

### Property 7: Defense Weight Formulas
*For any* warrior with valid attributes, the defense weights SHALL be calculated as:
- Block: strength × 0.6 + (SP / MAX_SP × 100) × 0.4
- Parry: martial_arts × 0.7 + agility × 0.3
- Dodge: agility × 0.8 + (100 - courage) × 0.2
- Counter: courage × 0.7 + martial_arts × 0.3
**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

### Property 8: Defense Selection - Highest Weight
*For any* defender with calculated defense weights, the selected defense SHALL be the one with the highest weight value.
**Validates: Requirements 3.6**

### Property 9: Success Rate Formulas with Clamping
*For any* attacker-defender pair, the success rates SHALL be:
- Parry: clamp(40% + (defender_martial_arts - attacker_strength) × 1.5%, 5%, 95%)
- Dodge: clamp(50% + (defender_agility - attacker_martial_arts) × 1%, 5%, 95%)
- Counter: clamp(30% + (defender_composite - attacker_composite) × 1%, 5%, 95%)
Where defender_composite = martial_arts × 0.45 + agility × 0.45 + courage × 0.1
And attacker_composite = agility × 0.50 + martial_arts × 0.40 + courage × 0.1
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 10: Block Damage Calculation
*For any* block action between attacker and defender:
- Impact force SHALL equal √(attacker_strength × defender_strength) × 0.5
- Defender damage SHALL equal impact_force × (attacker_strength / defender_strength)
- Attacker recoil SHALL equal min(impact_force × (defender_strength / attacker_strength) × 0.3, base_damage × 0.5)
- Both parties' SP consumption SHALL equal their damage_taken × 0.5
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 11: Successful Defense Effects
*For any* successful defense action:
- Parry: SP cost = 5, courage change = +20
- Dodge: SP cost = 12, courage change = +30
- Counter: SP cost = 20, courage change = +40, attacker receives normal damage
**Validates: Requirements 5.5, 5.6, 5.7**

### Property 12: Failed Defense Penalties
*For any* failed defense action:
- Parry fail: SP cost = 20, courage change = -20, damage multiplier = 1.0×
- Dodge fail: SP cost = 25, courage change = -30, damage multiplier = 1.2×
- Counter fail: SP cost = 20, courage change = -40, damage multiplier = 1.5×
**Validates: Requirements 5.8, 5.9, 5.10**

### Property 13: Damage Calculation Formulas
*For any* attacker-defender pair:
- Attack power SHALL equal strength × 1.5 + martial_arts × 0.5
- Defense power SHALL equal strength × 0.5 + stamina_max × 0.5
- Base impact SHALL equal strength × 0.1
- Physical damage SHALL equal max(0, attack_power - defense_power × armor_penetration)
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 14: Damage Multiplier Conditions
*For any* damage calculation:
- When defender SP < 20% of MAX_SP, a 1.5× multiplier SHALL be applied
- When attacker courage > 80 AND defender courage < 30, a 1.2× multiplier SHALL be applied
**Validates: Requirements 6.5, 6.6**

### Property 15: Final Damage Range
*For any* final damage calculation, the result SHALL be within [(base × multipliers × 0.95), (base × multipliers × 1.05)].
**Validates: Requirements 6.7**

### Property 16: Clash Detection
*For any* set of warriors where two or more have AP >= AP_LIMIT, a clash SHALL be detected if and only if the AP difference between any two ready warriors is <= 20.
**Validates: Requirements 7.1**

### Property 17: Clash Damage Calculation
*For any* clash between two warriors:
- Both warriors SHALL receive damage
- Each warrior's damage SHALL equal √(enemy_strength × self_strength) × 0.5 × (enemy_strength / self_strength) × 2
- Each warrior's SP cost SHALL equal damage_taken × 0.3
**Validates: Requirements 7.2, 7.3, 7.4, 7.5**

### Property 18: Round Completion Logic
*For any* battle state, when attack_count equals alive_warrior_count, the round SHALL be marked complete, round_counter SHALL increment by 1, and attack_counter SHALL reset to 0.
**Validates: Requirements 8.1, 8.3**

### Property 19: Battle End Determination
*For any* battle state:
- If Team_A alive count = 0 AND Team_B alive count > 0, winner SHALL be "B"
- If Team_B alive count = 0 AND Team_A alive count > 0, winner SHALL be "A"
- If both teams alive count = 0, result SHALL be "draw"
- If rounds >= 100, winner SHALL be the team with higher total HP percentage
**Validates: Requirements 9.1, 9.2, 9.3, 9.4**

### Property 20: Courage Clamping
*For any* courage modification, the resulting courage value SHALL be clamped to [0, COURAGE_CAP (120)].
**Validates: Requirements 10.1**

### Property 21: Battle State Serialization Round-Trip
*For any* valid battle state, serializing to JSON and then deserializing SHALL produce an equivalent battle state with all warrior attributes and states preserved.
**Validates: Requirements 11.1, 11.2, 11.3**

## Error Handling

### 输入验证
- 武将属性必须在有效范围内（1-100）
- 队伍必须至少有一名武将
- 不允许同队武将互相攻击

### 边界条件
- HP/SP不能为负数，最小为0
- 胆气值限制在0-120范围内
- 成功率限制在5%-95%范围内
- 伤害最小为0

### 异常处理
```python
class BattleError(Exception):
    """战斗系统基础异常"""
    pass

class InvalidWarriorError(BattleError):
    """无效武将配置"""
    pass

class InvalidTeamError(BattleError):
    """无效队伍配置"""
    pass
```

## Testing Strategy

### 单元测试
使用pytest进行单元测试，覆盖：
- 各公式计算的正确性
- 边界条件处理
- 状态转换逻辑

### 属性测试
使用Hypothesis库进行属性测试，验证：
- 所有正确性属性（Property 1-21）
- 每个属性测试运行至少100次迭代
- 测试注释格式：`**Feature: warrior-duel-system, Property {number}: {property_text}**`

### 测试文件结构
```
tests/
├── test_warrior.py          # 武将类测试
├── test_defense_system.py   # 防御系统测试
├── test_damage_system.py    # 伤害系统测试
├── test_clash_system.py     # 拼刀系统测试
├── test_battle_engine.py    # 战斗引擎测试
├── test_serialization.py    # 序列化测试
└── conftest.py              # 共享fixtures和生成器
```

### Hypothesis生成器策略
```python
from hypothesis import strategies as st

# 武将属性生成器
warrior_attributes = st.fixed_dictionaries({
    "martial_arts": st.integers(min_value=1, max_value=100),
    "agility": st.integers(min_value=1, max_value=100),
    "strength": st.integers(min_value=1, max_value=100),
    "courage": st.integers(min_value=0, max_value=120),
    "stamina_max": st.integers(min_value=1, max_value=5000),
})

# 武将状态生成器
warrior_state = st.fixed_dictionaries({
    "hp": st.integers(min_value=0, max_value=MAX_HP),
    "sp": st.integers(min_value=0, max_value=MAX_SP),
    "ap": st.floats(min_value=0, max_value=AP_LIMIT * 2),
})
```
