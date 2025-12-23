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

如果还没有安装 uv，请先安装：

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

## 📚 文档（DOCX）

- 说明：当前仓库根目录未检出任何 .docx 文档可供链接。如果你本地已有这些文档但尚未提交到仓库，请将其添加后我可以把它们在此处逐一列出并补充简要描述。
- 临时参考：你也可以先查看项目内的设计与技术文档目录：[docs/](docs/)

## 🌿 其他分支

- 可用分支：目前仓库包含 `master` 与 `delta` 分支（当前默认分支可能为 `master`，而 `delta` 为并行开发分支）。
- 切换体验：

```bash
git fetch --all
git checkout delta
```

如需我在 README 中对 `delta` 分支内容做更具体的简介，请告知关注点（例如：功能实验、UI 改动、数据结构调整等）。

## 📚 文档（DOCX）

- 说明：当前仓库根目录未检出任何 .docx 文档可供链接。如果你本地已有这些文档但尚未提交到仓库，请将其添加后我可以把它们在此处逐一列出并补充简要描述。
- 临时参考：你也可以先查看项目内的设计与技术文档目录：[docs/](docs/)

## 🌿 其他分支

- 可用分支：目前仓库包含 `master` 与 `delta` 分支（当前默认分支可能为 `master`，而 `delta` 为并行开发分支）。
- 切换体验：

```bash
git fetch --all
git checkout delta
```

如需我在 README 中对 `delta` 分支内容做更具体的简介，请告知关注点（例如：功能实验、UI 改动、数据结构调整等）。

## 📄 License

MIT
