# 《算界旅人》技术架构 (v4.0 - Textual TUI & ECS)

本文档定义了基于 **Textual** 框架和 **ECS (Entity Component System)** 架构的全新工程方案。
本项目将完全摒弃图形库 (pygame)，转而使用 Python 最先进的 TUI (Text User Interface) 框架 **Textual**，从零构建一个视觉和操作体验复刻 **Helix Editor** 的终端 RPG 游戏。

## 1. 核心技术栈 (Tech Stack)

| 模块 | 库/工具 | 版本要求 | 说明 |
| :--- | :--- | :--- | :--- |
| **UI/Engine** | **Textual** | 0.70.0+ | 核心 TUI 框架，提供 CSS 布局、事件循环和终端渲染。 |
| **Architecture** | **esper** | 3.0+ | 轻量级 ECS 框架，管理游戏逻辑实体与系统。 |
| **Rich Text** | **Rich** | 13.0+ | (Textual 内置) 处理彩色文本、表格、Markdown 渲染。 |
| **Data Validation** | **pydantic** | 2.0+ | 强类型数据模型定义与校验。 |
| **Storage** | **sqlite3** | - | 标准库，用于存档管理。 |

---

## 2. 视觉与交互风格 (Visual & Interaction Style)

*   **视觉风格**: **Native Terminal**。利用终端的原生字符渲染，结合 Textual 的 CSS 样式引擎，实现现代化的 TUI 界面。
*   **交互哲学**: **Helix Editor 复刻**。
    *   **Modal Editing**: 区分 Normal Mode (浏览/移动), Command Mode (指令), Insert Mode (交互/输入)。
    *   **Selection -> Action**: 先移动光标选中对象，再输入指令进行操作。
    *   **Key Driven**: 全键盘操作，无鼠标依赖。

---

## 3. 架构设计 (Architecture)

### 3.1 混合架构 (Hybrid Architecture)
我们将 **Textual (App/Widget)** 与 **Esper (ECS)** 结合使用。

*   **Textual App**: 负责主循环、输入事件捕获、屏幕切换 (Screen Management) 和 UI 布局渲染。
*   **ECS World**: 作为一个独立的逻辑核心运行。
    *   **Input Bridge**: Textual 捕获按键 -> 转发给 ECS `InputSystem`。
    *   **Render Bridge**: ECS `RenderSystem` 计算出的网格状态 -> 更新 Textual 的 `GameGrid` Widget。

### 3.2 目录结构 (Project Structure)

```text
UJN_AI_Final/
├── assets/                 # 资源
│   ├── data/               # JSON 数据 (items, enemies, skills, talents)
│   ├── maps/               # 文本地图 (.txt)
│   └── tcss/               # Textual CSS 样式表
├── src/                    # 源代码
│   ├── app.py              # Textual App 入口 (UI 主循环)
│   ├── screens/            # Textual 屏幕
│   │   ├── main_menu.py    # 主菜单
│   │   ├── game_screen.py  # 游戏主界面 (探索)
│   │   ├── combat.py       # 战斗界面
│   │   └── inventory.py    # 背包/装备界面
│   ├── widgets/            # 自定义 Widget
│   │   ├── game_grid.py    # 地图网格渲染器
│   │   ├── status_bar.py   # 状态栏
│   │   ├── command_line.py # 命令行输入
│   │   └── picker.py       # Helix 风格选择器
│   ├── components/         # [ECS] 组件
│   │   ├── base.py         # Transform, Glyph, Velocity
│   │   ├── combat.py       # Stats (HP/EP/ATK...), Health, Mana
│   │   ├── equipment.py    # EquipmentSlot, Inventory
│   │   ├── skills.py       # SkillBook, Cooldown
│   │   └── ai.py           # EnemyAI
│   ├── systems/            # [ECS] 系统
│   │   ├── input.py        # 输入处理
│   │   ├── movement.py     # 移动与碰撞
│   │   ├── render.py       # 网格计算
│   │   ├── combat.py       # 战斗逻辑 (回合管理)
│   │   └── interaction.py  # 交互 (NPC, 宝箱)
│   ├── data/               # 数据层
│   │   ├── models.py       # Pydantic 模型 (Item, Skill)
│   │   ├── database.py     # SQLite 封装
│   │   └── loader.py       # JSON 加载器
│   └── utils/              # 工具函数
├── main.py                 # 启动脚本
└── pyproject.toml          # 依赖配置
```

---

## 4. UI 系统详解 (UI System)

利用 Textual 的 Widget 和 CSS 系统复刻 Helix 界面。

### 4.1 布局 (Layout)
*   **Main Screen**: 使用 `Vertical` 布局。
    *   `Header`: (可选) 显示游戏标题。
    *   `GameView`: 占据主要空间，包含 `GameGrid` (地图显示)。
    *   `StatusBar`: 倒数第二行，显示模式、文件名(地图名)、光标位置。
    *   `CommandLine`: 最底行，用于输入 `:` 命令或显示提示。

### 4.2 关键组件 (Widgets)
*   **GameGrid (Widget)**:
    *   使用 Rich 的 `Table` 或 `Text` 对象渲染字符网格。
    *   通过 `watch` 机制响应 ECS 的数据变化。
*   **HelixPicker (ModalScreen)**:
    *   复刻 Helix 的 `Space` 菜单或文件选择器。
    *   居中弹出的列表，支持模糊搜索过滤。
    *   使用 CSS 实现边框和高亮效果。
*   **StatusBar (Widget)**:
    *   动态显示当前模式 (NORMAL/COMMAND) 的背景色 (如 Normal=Blue, Command=Red)。

---

## 5. 游戏逻辑 (Game Logic)

### 5.1 ECS 系统
*   **InputSystem**: 接收 Textual 传来的按键事件 (如 `h/j/k/l`)，更新玩家 `Velocity` 或 `Action` 组件。
*   **MovementSystem**: 处理碰撞检测和坐标更新。
*   **RenderSystem**: 并不直接 print，而是生成一个 2D 字符矩阵 (Buffer)，然后调用 `GameGrid.update_grid(buffer)` 刷新 UI。

### 5.2 战斗系统
*   **CombatScreen**: 当遭遇敌人时，Textual 切换到 `CombatScreen`。
*   **UI**: 左侧显示战斗日志 (Log)，右侧显示状态面板和操作菜单。
*   **流程**: 依然采用回合制，通过菜单选择 Skill/Item。

---

## 6. 数据架构 (Data Architecture)

### 6.1 静态数据 (Static Data - JSON)
定义游戏的基础规则和对象模板，使用 Pydantic 进行校验。

*   `items.json`: 物品定义 (ID, Name, Type, Era, Stats, Effects)。
*   `skills.json`: 技能定义 (ID, Name, Cost, Cooldown, Effect)。
*   `enemies.json`: 敌人模板 (ID, Name, BaseStats, DropTable)。
*   `talents.json`: 天赋树定义 (TreeID, Nodes, Requirements)。
*   `era_tech.json`: 时代科技树定义。

### 6.2 持久化数据 (Persistent Data - SQLite)
存储玩家进度和世界状态。

**Schema 设计:**

1.  **`save_metadata`**: 存档元数据
    *   `id` (PK), `timestamp`, `play_time`, `current_location`
2.  **`player_stats`**: 玩家基础数值
    *   `save_id` (FK), `level`, `exp`, `hp`, `ep`, `base_atk`, `base_def`, `base_spd`, `base_fcs`, `money`
3.  **`inventory`**: 背包物品实例
    *   `id` (PK), `save_id` (FK), `item_id` (Ref JSON), `count`, `quality`, `era_modifier`
4.  **`equipment`**: 装备状态
    *   `save_id` (FK), `slot_name` (head, body, weapon, acc1, acc2), `inventory_id` (FK)
5.  **`skills_learned`**: 已习得技能
    *   `save_id` (FK), `skill_id` (Ref JSON), `level`
6.  **`world_state`**: 世界标志位 (任务/宝箱)
    *   `save_id` (FK), `key` (String), `value` (String/Int)

## 7. 开发路线 (Roadmap)

1.  **Phase 1: TUI Skeleton**: 搭建 Textual App，实现 Helix 风格的布局 (Status Bar, Command Line)。
2.  **Phase 2: ECS Integration**: 引入 Esper，实现基本的移动 (Movement) 和地图渲染 (Render to Widget)。
3.  **Phase 3: Interaction**: 实现 `Space` 菜单 (Picker) 和 `:` 命令模式。
4.  **Phase 4: Gameplay**: 战斗系统、背包系统、对话系统。

