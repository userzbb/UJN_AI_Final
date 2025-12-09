# 游戏数据存储进阶方案指南

当你的游戏变得复杂（拥有多个存档槽、庞大的物品数据库、复杂的地图状态）时，简单的 JSON + LocalStorage 方案可能会遇到性能瓶颈或容量限制。以下是针对 Python (Pygame) + Web (Pygbag) 环境的进阶数据存储方案。

## 1. 存档管理策略 (Save Slots)

在技术升级之前，首先要在逻辑层面上管理存档。

*   **多存档槽设计**: 不要只用一个 `save.json`。
    *   **文件命名**: 使用 `save_0.json`, `save_1.json`, `auto_save.json`。
    *   **元数据 (Metadata)**: 创建一个单独的 `global_save.json` 或 `manifest.json`，只存储存档的摘要信息（如：存档时间、玩家等级、当前地图），用于在“加载游戏”菜单中快速显示，而不需要读取整个庞大的存档文件。

## 2. 浏览器端 (Web/Pygbag) 进阶方案

浏览器的 `LocalStorage` 通常只有 5MB 的限制，且只能存字符串。

### A. IndexedDB (推荐)
这是浏览器内置的 NoSQL 数据库，容量大（通常几百 MB 到 GB），支持二进制数据。

*   **Python 实现**: 在 Pygbag 环境下，你可以通过 `platform.window` 访问 JS 的 `IndexedDB` API，或者使用 Python 的包装库。
*   **优点**: 容量大，异步读写不卡顿。
*   **缺点**: API 比较复杂，需要写一些 Python <-> JS 的桥接代码。

### B. SQLite (Wasm 版)
SQLite 是游戏界的标准数据库。

*   **技术栈**: `sqlite3` (Python 标准库)
*   **Web 适配**: Pygbag/Emscripten 环境通常支持将虚拟文件系统映射到 IndexedDB (IDBFS)。
    *   这意味着你可以像在桌面端一样使用 `sqlite3` 读写 `.db` 文件，底层由 Emscripten 自动同步到浏览器的 IndexedDB。
*   **优点**: 极其强大的查询能力（SQL），代码与桌面端完全通用。
*   **缺点**: 需要确保文件系统同步机制正确配置，否则刷新页面可能丢失数据。

## 3. 桌面端 / 通用进阶方案

### A. SQLite
*   **适用场景**: 拥有大量物品数据、怪物属性、对话文本的 RPG。
*   **用法**: 将静态数据（物品属性）和动态数据（玩家背包）分开。
    *   `static_data.db`: 只读，存放游戏设定。
    *   `user_save.db`: 读写，存放玩家进度。

### B. 二进制序列化 (Pickle / MsgPack)
如果 JSON 文件太大（几十 MB），解析速度会变慢。

*   **Pickle**: Python 自带，支持保存任意 Python 对象。
    *   *警告*: 安全性差，不要加载陌生人的 pickle 文件。
*   **MsgPack**: 类似 JSON 但更紧凑、更快的二进制格式。
    *   **库**: `msgpack-python`
    *   **优点**: 体积小，速度快，跨语言。

## 4. 云存档 (Cloud Save)

如果你希望玩家在不同设备（电脑浏览器 <-> 手机浏览器）之间同步进度。

*   **技术栈**: Python `requests` / `aiohttp` + 后端 API (Flask/Django/FastAPI)。
*   **流程**:
    1.  用户登录/注册。
    2.  游戏将 JSON/二进制数据 POST 到你的服务器。
    3.  服务器存入 MySQL/PostgreSQL/MongoDB。
*   **注意**: 在 WebAssembly 环境中，网络请求受到 CORS (跨域) 限制，需要配置好服务器头。

---

## 总结推荐

### 阶段一：优化 JSON (当前推荐)
如果你的存档还没超过 1MB：
1.  继续使用 JSON。
2.  实现**多存档槽**逻辑（`save_1`, `save_2`）。
3.  将静态数据（如物品详细描述）硬编码在代码里或单独的只读 JSON 中，存档只存 ID 和数量，减小体积。

### 阶段二：引入 SQLite
当你有成千上万个游戏对象，或者需要复杂的查询（"查找背包里所有类型为'武器'且等级>5的物品"）时：
1.  使用 Python 自带的 `sqlite3`。
2.  在 Web 端利用 Pygbag 的文件系统同步功能。

### 阶段三：云同步
当你准备正式发布并希望长期运营时，搭建一个简单的后端服务来托管存档。
