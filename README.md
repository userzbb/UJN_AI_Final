# TimeStack: 计算史诗 TUI (TimeStack: A Computing History TUI)

![TimeStack Banner](https://via.placeholder.com/800x200?text=TimeStack:+A+Computing+History+TUI)

> **"历史不是一条线，而是一个栈。"**

**TimeStack** 是一款基于终端的角色扮演游戏 (TUI RPG)。你将扮演一名 **调试者 (Debugger)**，穿越层层堆叠的计算历史纪元。从巴贝奇差分机的机械齿轮，到微芯片时代的硅谷平原，你的任务是修复被破坏的技术时间线。

本项目基于 [Textual](https://github.com/Textualize/textual) 和 [Esper](https://github.com/benmoran56/esper) 构建。

## 🎮 游戏特色

*   **Vim 风格操控**: 使用 `h`, `j`, `k`, `l` 和模态命令进行移动与交互。键盘战士的终极浪漫。
*   **层叠世界**: 探索截然不同的计算时代（机械时代、电子管时代、晶体管时代、网络时代）。
*   **ECS 架构**: 采用实体组件系统 (Entity Component System)，逻辑灵活高效。
*   **复古 TUI**: 精美的高性能终端界面，支持真彩色。

## 🚀 快速开始

### 前置要求

*   Python 3.10+
*   支持真彩色 (True Color) 的终端 (如 Alacritty, Kitty, iTerm2, Windows Terminal, VS Code Terminal)
*   已安装 `uv` (推荐) 或 `pip`

### 安装与运行

1.  克隆仓库：
    ```bash
    git clone https://github.com/userzbb/UJN_AI_Final.git
    cd UJN_AI_Final
    ```

2.  安装依赖并运行：

    **使用 uv (推荐):**
    ```bash
    # 同步环境
    uv sync
    
    # 运行游戏
    uv run main.py
    ```

    **使用 pip:**
    ```bash
    pip install -r requirements.txt
    python main.py
    ```

## 🕹️ 操作指南

| 按键 | 动作 |
| :--- | :--- |
| `h` `j` `k` `l` | 左 / 下 / 上 / 右 移动 |
| `Space` | 打开 **操作菜单** (装备, 存档/读档) |
| `:` | 进入 **命令模式** |
| `:w` | 保存游戏 |
| `:q` | 退出到主菜单 |

## 🤝 参与贡献

我们正在打造一份致敬计算机发展史的开源献礼，我们需要 **你** 的加入！

无论你是 Python 魔法师、历史爱好者，还是像素艺术家（或者 ASCII 艺术家？），这里都有你的位置。

### 为什么要加入？

*   **学习 TUI 开发**: 掌握 `Textual`，这是目前最前沿的 Python 终端应用框架。
*   **ECS 模式**: 获得在 Python 中使用实体组件系统的实战经验。
*   **创意自由**: 设计基于真实历史计算机（如 ENIAC, Colossus）的新敌人（Bugs!）、道具（Patches!）或地图。

### 开发路线图 (Roadmap)

- [x] 核心引擎 (移动, 渲染, ECS)
- [x] 存档/读档系统 (SQLite)
- [x] 装备系统
- [ ] **战斗系统**: 回合制调试战斗。
- [ ] **内容填充**: 更多时代 (机械时代, 电子管时代)。
- [ ] **NPC**: 历史人物 (如 Ada Lovelace, Alan Turing)。

### 如何加入

1.  Fork 本仓库。
2.  认领一个 Issue 或提出新功能。
3.  提交 Pull Request!

让我们一起调试历史！ 🐛🔨

## 📄 许可证

MIT License
