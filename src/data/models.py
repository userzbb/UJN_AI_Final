"""
数据模型定义
使用 Pydantic 进行数据校验
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """用户模型"""
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    current_path: str = "/"


class VFSNode(BaseModel):
    """虚拟文件系统节点模型"""
    id: int
    user_id: int
    parent_id: Optional[int] = None
    name: str
    is_directory: bool = False
    content: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserSession(BaseModel):
    """用户会话信息"""
    user_id: int
    username: str
    current_path: str = "/"
    current_node_id: Optional[int] = None  # 当前目录的节点ID，None 表示根目录


# ==================== 游戏静态数据模型 ====================

class VisualInfo(BaseModel):
    """视觉信息定义"""
    name: str
    symbol: str
    color: str
    description: str = ""


class Stats(BaseModel):
    """属性数值"""
    hp: int = 0
    ep: int = 0
    atk: int = 0
    def_: int = Field(default=0, alias="def")
    spd: int = 0
    fcs: int = 0  # 专注值

    class Config:
        populate_by_name = True


class ItemEffect(BaseModel):
    """物品效果"""
    type: str
    value: float = 0
    condition: Optional[str] = None


class ItemModel(BaseModel):
    """物品模型"""
    id: str
    name: str
    symbol: str = "?"
    color: str = "white"
    type: str  # weapon, armor, consumable, material, key
    era: str = "universal"
    rarity: str = "common"
    description: str = ""
    stats: Optional[Stats] = None
    effects: list[ItemEffect] = []
    price: int = 0


class DropInfo(BaseModel):
    """掉落信息"""
    item_id: str
    chance: float = 1.0
    count_min: int = 1
    count_max: int = 1


class EnemyModel(BaseModel):
    """敌人模型"""
    id: str
    name: str
    symbol: str = "?"
    color: str = "red"
    type: str = "normal"
    level: int = 1
    stats: Stats
    skills: list[str] = []
    drops: list[DropInfo] = []
    ai_behavior: str = "passive"


class SkillEffect(BaseModel):
    """技能效果"""
    type: str
    power: float = 1.0
    hit_count: int = 1
    duration: int = 0


class SkillCost(BaseModel):
    """技能消耗"""
    hp: int = 0
    ep: int = 0


class SkillModel(BaseModel):
    """技能模型"""
    id: str
    name: str
    type: str = "active"  # active, passive
    cost: SkillCost = SkillCost()
    cooldown: int = 0
    target: str = "single_enemy"
    description: str = ""
    effect: SkillEffect
