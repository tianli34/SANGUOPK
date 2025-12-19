# Requirements Document

## Introduction

本系统模拟三国武将之间的自动战斗对决，采用基于行动点(AP)的回合制战斗机制。系统支持多种防御策略（硬接、卸力、闪避、反击）、拼刀系统、以及完整的伤害计算体系。战斗为自动进行，AI根据武将属性选择最优防御策略。

## Glossary

- **武将 (Warrior)**: 参与战斗的角色单位，拥有五维属性和实时状态
- **行动点 (AP - Action Points)**: 累积到阈值后触发攻击的数值
- **体力 (SP - Stamina Points)**: 影响攻速和防御行动的资源
- **生命值 (HP - Health Points)**: 归零则武将阵亡
- **胆气 (Courage)**: 影响反击倾向和士气碾压的属性
- **Tick**: 战斗时间单位，每Tick为0.05秒
- **拼刀 (Clash)**: 多人同时达到AP阈值时触发的特殊战斗
- **硬接 (Block)**: 正面承受攻击的防御方式
- **卸力 (Parry)**: 化解攻击力道的防御方式
- **闪避 (Dodge)**: 躲避攻击的防御方式
- **反击 (Counter)**: 防守同时发动攻击的防御方式
- **回合 (Round)**: 攻击次数达到存活人数时视为一回合

## Requirements

### Requirement 1

**User Story:** As a game designer, I want to define warrior attributes, so that each warrior has unique combat characteristics.

#### Acceptance Criteria

1. WHEN a warrior is created THEN the Warrior_System SHALL initialize five core attributes: martial_arts, agility, strength, courage, and stamina_max
2. WHEN a warrior is created THEN the Warrior_System SHALL initialize runtime states: HP to MAX_HP (10000), SP to MAX_SP (5000), AP to 0, and is_alive to true
3. WHEN calculating attack speed THEN the Warrior_System SHALL apply the formula: (100 + agility × 2) × min(1, (current_SP / MAX_SP) / 0.5)
4. WHEN a warrior's HP reaches zero THEN the Warrior_System SHALL set is_alive to false

### Requirement 2

**User Story:** As a game designer, I want an AP-based action system, so that warriors take turns attacking based on their speed.

#### Acceptance Criteria

1. WHEN a tick occurs THEN the AP_System SHALL increase each alive warrior's AP by: attack_speed × tick_rate (0.05)
2. WHEN a warrior's AP reaches or exceeds AP_LIMIT (500) THEN the AP_System SHALL mark the warrior as ready to attack
3. WHEN a warrior completes an attack THEN the AP_System SHALL reset that warrior's AP to zero
4. WHEN selecting a target THEN the AP_System SHALL prioritize the enemy with the lowest current HP

### Requirement 3

**User Story:** As a game designer, I want an AI-driven defense selection system, so that warriors automatically choose optimal defense strategies.

#### Acceptance Criteria

1. WHEN a warrior is attacked THEN the Defense_System SHALL calculate weights for all four defense options using attribute-based formulas
2. WHEN calculating block weight THEN the Defense_System SHALL apply: strength × 0.6 + SP_percentage × 0.4
3. WHEN calculating parry weight THEN the Defense_System SHALL apply: martial_arts × 0.7 + agility × 0.3
4. WHEN calculating dodge weight THEN the Defense_System SHALL apply: agility × 0.8 + (100 - courage) × 0.2
5. WHEN calculating counter weight THEN the Defense_System SHALL apply: courage × 0.7 + martial_arts × 0.3
6. WHEN defense weights are calculated THEN the Defense_System SHALL select the defense with the highest weight

### Requirement 4

**User Story:** As a game designer, I want defense success rate calculations, so that defense outcomes are determined by attribute comparisons.

#### Acceptance Criteria

1. WHEN a parry is attempted THEN the Defense_System SHALL calculate success rate: 40% + (defender_martial_arts - attacker_strength) × 1.5%, clamped to 5%-95%
2. WHEN a dodge is attempted THEN the Defense_System SHALL calculate success rate: 50% + (defender_agility - attacker_martial_arts) × 1%, clamped to 5%-95%
3. WHEN a counter is attempted THEN the Defense_System SHALL calculate success rate: 30% + (defender_composite - attacker_composite) × 1%, clamped to 5%-95%
4. WHEN calculating defender composite for counter THEN the Defense_System SHALL apply: martial_arts × 0.45 + agility × 0.45 + courage × 0.1
5. WHEN calculating attacker composite for counter THEN the Defense_System SHALL apply: agility × 0.50 + martial_arts × 0.40 + courage × 0.1

### Requirement 5

**User Story:** As a game designer, I want defense outcome effects, so that successful and failed defenses have appropriate consequences.

#### Acceptance Criteria

1. WHEN a block occurs THEN the Defense_System SHALL calculate impact_force: √(attacker_strength × defender_strength) × 0.5
2. WHEN a block occurs THEN the Defense_System SHALL apply defender damage: impact_force × (attacker_strength / defender_strength)
3. WHEN a block occurs THEN the Defense_System SHALL apply attacker recoil: impact_force × (defender_strength / attacker_strength) × 0.3, capped at base_damage × 0.5
4. WHEN a block occurs THEN the Defense_System SHALL consume SP from both parties: damage_taken × 0.5
5. WHEN a parry succeeds THEN the Defense_System SHALL consume 5 SP and increase courage by 20
6. WHEN a dodge succeeds THEN the Defense_System SHALL consume 12 SP and increase courage by 30
7. WHEN a counter succeeds THEN the Defense_System SHALL consume 20 SP, increase courage by 40, and deal normal attack damage to the attacker
8. WHEN a parry fails THEN the Defense_System SHALL consume 20 SP, decrease courage by 20, and apply 1.0× damage
9. WHEN a dodge fails THEN the Defense_System SHALL consume 25 SP, decrease courage by 30, and apply 1.2× damage
10. WHEN a counter fails THEN the Defense_System SHALL consume 20 SP, decrease courage by 40, and apply 1.5× damage

### Requirement 6

**User Story:** As a game designer, I want a damage calculation system, so that combat damage is computed based on attributes and modifiers.

#### Acceptance Criteria

1. WHEN calculating attack power THEN the Damage_System SHALL apply: strength × 1.5 + martial_arts × 0.5
2. WHEN calculating defense power THEN the Damage_System SHALL apply: strength × 0.5 + stamina_max × 0.5
3. WHEN calculating base impact THEN the Damage_System SHALL apply: strength × 0.1
4. WHEN calculating physical damage THEN the Damage_System SHALL apply: max(0, attack_power - defense_power × armor_penetration)
5. WHEN applying damage multipliers THEN the Damage_System SHALL apply 1.5× for stamina_collapse (SP < 20%)
6. WHEN applying damage multipliers THEN the Damage_System SHALL apply 1.2× for morale_crush (attacker_courage > 80 AND defender_courage < 30)
7. WHEN calculating final damage THEN the Damage_System SHALL apply: (physical_damage + base_impact) × multipliers × random_float(0.95, 1.05)

### Requirement 7

**User Story:** As a game designer, I want a clash system, so that simultaneous attacks create dramatic confrontations.

#### Acceptance Criteria

1. WHEN two or more warriors reach AP threshold simultaneously THEN the Clash_System SHALL check if AP difference is within 20 points
2. WHEN a clash is triggered THEN the Clash_System SHALL have both participants attack each other simultaneously
3. WHEN calculating clash damage THEN the Clash_System SHALL apply impact_force: √(enemy_strength × self_strength) × 0.5
4. WHEN calculating clash damage THEN the Clash_System SHALL apply damage: impact_force × (enemy_strength / self_strength) × 2
5. WHEN a clash occurs THEN the Clash_System SHALL consume SP from both parties: damage_taken × 0.3

### Requirement 8

**User Story:** As a game designer, I want a round tracking system, so that battle progress is measured in rounds.

#### Acceptance Criteria

1. WHEN attack count equals the number of alive warriors THEN the Round_System SHALL mark the round as complete
2. WHEN a round completes THEN the Round_System SHALL output a battle summary
3. WHEN a round completes THEN the Round_System SHALL increment round counter and reset attack counter

### Requirement 9

**User Story:** As a game designer, I want battle end conditions, so that combat concludes with clear victory or draw outcomes.

#### Acceptance Criteria

1. WHEN Team_A has zero alive warriors AND Team_B has alive warriors THEN the Battle_System SHALL declare Team_B as winner
2. WHEN Team_B has zero alive warriors AND Team_A has alive warriors THEN the Battle_System SHALL declare Team_A as winner
3. WHEN both teams have zero alive warriors simultaneously THEN the Battle_System SHALL declare a draw
4. WHEN maximum rounds (100) are reached without a winner THEN the Battle_System SHALL compare total remaining HP percentage and declare the higher team as winner
5. WHEN checking battle end THEN the Battle_System SHALL perform the check at the end of each tick to capture simultaneous deaths

### Requirement 10

**User Story:** As a game designer, I want courage to be capped, so that the courage attribute stays within reasonable bounds.

#### Acceptance Criteria

1. WHEN courage is modified THEN the Warrior_System SHALL clamp the value between 0 and COURAGE_CAP (120)

### Requirement 11

**User Story:** As a game designer, I want battle state serialization, so that battle states can be saved and restored.

#### Acceptance Criteria

1. WHEN serializing battle state THEN the Serialization_System SHALL encode all warrior attributes and states to JSON format
2. WHEN deserializing battle state THEN the Serialization_System SHALL restore all warrior attributes and states from JSON format
3. WHEN round-trip serialization occurs THEN the Serialization_System SHALL produce an equivalent battle state
