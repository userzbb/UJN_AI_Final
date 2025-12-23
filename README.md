# 《算界旅人》 - 终端 RPG 游戏

一款基于 **Textual** 框架的 TUI (Text User Interface) 终端 RPG 游戏。

在「算界」这个计算之域中展开你的冒险！

## ✨ 特性

- 🖥️ **终端模拟器界面** - 类 Linux 终端的交互体验
- 👤 **用户系统** - 注册、登录，每个用户拥有独立存档
- 📁 **虚拟文件系统** - 完整的 CRUD 操作 (创建/读取/修改/删除)
- 💾 **SQLite 持久化** - 自动保存游戏进度

## 🛠️ 环境要求

- **Python** >= 3.12
- **uv** (推荐的 Python 包管理器)

## 🚀 快速开始

### 1. 安装 uv

如果还没有安装 uv，请先安装（详见 [uv 官网](https://docs.astral.sh/uv/)）：

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd UJN_AI_Final
```

### 3. 安装依赖

```bash
# 创建虚拟环境并安装依赖
uv sync
```

### 4. 运行游戏

```bash
uv run python main.py
```

或者先激活虚拟环境再运行：

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
python main.py

# macOS / Linux
source .venv/bin/activate
python main.py
```

## 📖 游戏命令

### 用户命令

| 命令                       | 说明         |
| -------------------------- | ------------ |
| `register <用户名> <密码>` | 注册新账户   |
| `login <用户名> <密码>`    | 登录         |
| `logout`                   | 登出         |
| `whoami`                   | 显示当前用户 |

### 文件命令 (需登录)

| 命令                    | 说明          |
| ----------------------- | ------------- |
| `pwd`                   | 显示当前路径  |
| `cd <路径>`             | 切换目录      |
| `ls [路径]`             | 列出目录内容  |
| `mkdir <名称>`          | 创建目录      |
| `touch <文件名>`        | 创建空文件    |
| `cat <文件名>`          | 查看文件内容  |
| `write <文件名> <内容>` | 写入文件      |
| `rm [-r] <名称>`        | 删除文件/目录 |
| `mv <源> <目标>`        | 重命名        |
| `tree`                  | 显示目录树    |

### 系统命令

| 命令    | 说明     |
| ------- | -------- |
| `help`  | 显示帮助 |
| `clear` | 清空终端 |
| `exit`  | 退出游戏 |

## 📦 技术栈

- **Textual** - TUI 框架
- **Esper** - ECS 架构
- **Pydantic** - 数据校验
- **SQLite** - 数据持久化

## 📁 项目结构

```
UJN_AI_Final/
├── main.py              # 启动入口
├── pyproject.toml       # 项目配置
├── save/                # 存档目录 (自动生成)
├── assets/
│   └── tcss/            # Textual CSS 样式
└── src/
    ├── app.py           # 主应用
    ├── widgets/         # UI 组件
    ├── systems/         # 游戏系统 (认证、文件系统)
    └── data/            # 数据层 (数据库、模型)
```

## 📚 开发文档

项目设计与技术文档位于 [docs/](docs/) 目录，包含项目开发的思路与架构设计：

- **设计文档** [docs/design/](docs/design/)

  - [CORE_GAMEPLAY.md](docs/design/CORE_GAMEPLAY.md) - 核心玩法设计
  - [ERA_MECHANICAL_COMPUTING.md](docs/design/ERA_MECHANICAL_COMPUTING.md) - 机械计算时代设定
  - [MAIN_STORY.md](docs/design/MAIN_STORY.md) - 主线剧情

- **技术文档** [docs/tech/](docs/tech/)
  - [GAME_DATA_SCHEMA.md](docs/tech/GAME_DATA_SCHEMA.md) - 游戏数据结构
  - [TECHNICAL_DESIGN.md](docs/tech/TECHNICAL_DESIGN.md) - 技术设计文档

## 🌿 分支说明

- **`master`** - 稳定版本分支
- **`delta`** - 当前开发分支（你现在所在的分支）

## 📄 License

MIT
