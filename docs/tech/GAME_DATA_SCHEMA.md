# 游戏数据规范 (Game Data Schema)

本文档定义了《算界旅人》的数据结构规范。
项目采用 **Pydantic** 进行静态数据 (JSON) 的定义与校验，采用 **SQLite** 存储动态存档数据。

## 1. 静态数据 (Static Data - JSON)

所有静态游戏内容存储在 `assets/data/` 目录下。
加载时，系统将使用 Pydantic 模型验证 JSON 文件的完整性。

### 1.1 通用视觉定义 (Visual Definition)

由于采用 TUI 界面，所有实体不再使用图片路径，而是定义字符与颜色。

```python
class VisualInfo(BaseModel):
    name: str           # 显示名称
    symbol: str         # 渲染字符 (如 "@", "⚔", "G")
    color: str          # Rich 风格颜色代码 (如 "red", "#ff00ff", "bold yellow")
    description: str    # 描述文本
```

### 1.2 物品 (Items)

文件路径: `assets/data/items.json`

```json
[
  {
    "id": "diff_blade_01",
    "name": "差分之刃",
    "symbol": "/",
    "color": "cyan",
    "type": "weapon",
    "era": "mechanical",
    "rarity": "rare",
    "description": "利用差分机齿轮原理制造的剑，对重复动作有加成。",
    "stats": {
      "atk": 15,
      "spd": -2
    },
    "effects": [
      {"type": "damage_boost", "condition": "repeat_attack", "value": 1.2}
    ],
    "price": 500
  },
  {
    "id": "steam_potion",
    "name": "高压蒸汽罐",
    "symbol": "!",
    "color": "red",
    "type": "consumable",
    "era": "mechanical",
    "description": "恢复 50 点 EP，但会产生过热状态。",
    "use_effect": {
      "restore_ep": 50,
      "add_status": "overheat"
    },
    "price": 50
  }
]
```

### 1.3 敌人 (Enemies)

文件路径: `assets/data/enemies.json`

```json
[
  {
    "id": "abacus_soldier",
    "name": "走火的算盘兵",
    "symbol": "A",
    "color": "yellow",
    "type": "mechanical",
    "level": 3,
    "stats": {
      "hp": 80,
      "atk": 12,
      "def": 5,
      "spd": 8
    },
    "skills": ["bead_shot", "charge"],
    "drops": [
      {"item_id": "wood_bead", "chance": 0.5},
      {"item_id": "broken_frame", "chance": 0.2}
    ],
    "ai_behavior": "aggressive" 
  }
]
```

### 1.4 技能 (Skills)

文件路径: `assets/data/skills.json`

```json
[
  {
    "id": "gear_slash",
    "name": "齿轮连击",
    "type": "active",
    "cost": {"ep": 10},
    "cooldown": 2,
    "target": "single_enemy",
    "effect": {
      "type": "physical_damage",
      "power": 1.5,
      "hit_count": 3
    },
    "visual_effect": {
      "symbol": "*",
      "color": "bold white",
      "pattern": "flash"
    }
  }
]
```

### 1.5 地图 (Maps)

地图不再是图片，而是纯文本文件与元数据的组合。

**元数据文件**: `assets/maps/map_manifest.json`
```json
{
  "factory_01": {
    "name": "废弃差分工厂",
    "file": "factory_01.txt",
    "width": 80,
    "height": 24,
    "era": "mechanical",
    "music": "bgm_factory"
  }
}
```

**地图文件**: `assets/maps/factory_01.txt`
使用 ASCII 字符绘制地形：
- `#`: 墙壁 (Wall)
- `.`: 地板 (Floor)
- `+`: 门 (Door)
- `~`: 水/液体 (Liquid)

```text
########################################
#......#..........#....................#
#......+..........+....................#
#......#..........#....................#
########################################
```

---

## 2. 动态数据 (Dynamic Data - SQLite)

存档数据存储在 `save/savegame.db` 中。

### 2.1 数据库表结构 (Schema)

#### `player_state` 表
存储玩家的基础属性和当前状态。

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `save_id` | INTEGER PK | 存档槽位 ID |
| `level` | INTEGER | 等级 |
| `current_hp` | INTEGER | 当前生命值 |
| `current_ep` | INTEGER | 当前能量值 |
| `map_id` | TEXT | 当前所在地图 ID |
| `pos_x` | INTEGER | X 坐标 |
| `pos_y` | INTEGER | Y 坐标 |
| `play_time` | INTEGER | 游戏时长 (秒) |

#### `inventory` 表
存储玩家背包物品。

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | INTEGER PK | 自增 ID |
| `save_id` | INTEGER FK | 关联存档 ID |
| `item_id` | TEXT | 物品 ID (对应 items.json) |
| `count` | INTEGER | 数量 |
| `is_equipped` | BOOLEAN | 是否已装备 |
| `slot` | TEXT | 装备槽位 (weapon, armor, accessory) |

#### `quest_progress` 表
存储任务状态。

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `save_id` | INTEGER FK | 关联存档 ID |
| `quest_id` | TEXT | 任务 ID |
| `status` | TEXT | 状态 (active, completed, failed) |
| `step_index` | INTEGER | 当前进行到的步骤索引 |

#### `world_flags` 表
存储世界状态标志 (如 Boss 是否被击败，宝箱是否开启)。

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `save_id` | INTEGER FK | 关联存档 ID |
| `flag_key` | TEXT | 标志键 (如 "boss_killed_01") |
| `value` | TEXT | 值 |

---

## 3. Pydantic 模型预览 (Python Code Preview)

在 `src/data/models.py` 中将实现如下模型：

```python
from pydantic import BaseModel
from typing import List, Optional, Dict

class Stats(BaseModel):
    hp: int = 0
    ep: int = 0
    atk: int = 0
    def_: int = 0  # 使用 def_ 避免关键字冲突
    spd: int = 0

class ItemModel(BaseModel):
    id: str
    name: str
    symbol: str
    color: str
    type: str
    era: str
    stats: Optional[Stats] = None
    price: int = 0

class EnemyModel(BaseModel):
    id: str
    name: str
    symbol: str
    color: str
    stats: Stats
    skills: List[str]
    ai_behavior: str
```
