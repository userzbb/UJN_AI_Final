# 本地游戏存储：SQLite 以外的选择

既然你的游戏只需在本地运行（包括浏览器端的本地环境），且希望寻找 SQLite 以外的方案，以下是几个非常适合 Python 开发者的**纯 Python** 数据库/存储方案。

这些方案的共同优点是：**无需安装额外的数据库软件（如 MySQL），且完美兼容 Pygbag (Web) 环境。**

## 1. TinyDB (最推荐的轻量级 NoSQL)

如果你喜欢 JSON 的灵活性，但又想要类似数据库的查询功能（比如“查找所有等级 > 5 的物品”），TinyDB 是最佳选择。

*   **类型**: 文档型数据库 (Document Oriented)
*   **原理**: 它本质上还是在读写 JSON 文件，但提供了一套强大的 Python API 来操作数据。
*   **优点**:
    *   **纯 Python 编写**: 完美兼容 Pygbag/WebAssembly，无需编译 C 扩展。
    *   **API 友好**: 用起来像操作 Python 列表和字典，不需要学 SQL 语句。
    *   **轻量**: 极其小巧。
*   **缺点**: 性能不如 SQLite，如果数据量达到几万条，速度会变慢（因为它每次都要读写整个文件）。
*   **代码示例**:
    ```python
    from tinydb import TinyDB, Query
    db = TinyDB('game_data.json')
    
    # 存数据
    db.insert({'type': 'weapon', 'name': 'Iron Sword', 'damage': 10})
    
    # 查数据
    Item = Query()
    sword = db.search(Item.name == 'Iron Sword')
    ```

## 2. Shelve (Python 标准库)

如果你只需要一个简单的“键值对”存储（类似字典），而且不想安装任何第三方库。

*   **类型**: 键值存储 (Key-Value Store)
*   **原理**: 它是 Python 自带的模块，用法和字典几乎一模一样，但数据会自动保存到文件里。底层使用 `pickle` 序列化。
*   **优点**:
    *   **内置**: Python 自带，无需 `uv add`。
    *   **简单**: 就像用字典一样 `data['player'] = ...`。
    *   **支持任意对象**: 可以直接存 Python 的类实例、列表等，不需要手动转 JSON。
*   **缺点**:
    *   **黑盒**: 生成的文件是二进制的，无法用文本编辑器打开查看。
    *   **查询弱**: 只能通过 Key (键) 来找数据，不能进行条件查询（比如不能直接“找所有攻击力>5的武器”）。
*   **代码示例**:
    ```python
    import shelve
    
    # 打开数据库（就像打开文件）
    with shelve.open('gamedata') as db:
        db['player_hp'] = 100
        db['inventory'] = ['sword', 'shield']
        
    # 下次读取
    with shelve.open('gamedata') as db:
        print(db['player_hp'])
    ```

## 3. Pickle (原生序列化)

虽然不是严格意义上的“数据库”，但对于单机游戏存档来说，它是最直接的方式。

*   **原理**: 将内存中的 Python 对象直接“冻结”成二进制文件。
*   **优点**: 极其快，开发极其简单。你可以把整个 `Game` 类直接存进去。
*   **缺点**:
    *   **安全性**: 千万不要加载别人发给你的 pickle 文件（可以执行恶意代码）。但如果是你自己生成的存档，这没问题。
    *   **版本兼容性**: 如果你修改了代码里的类结构（比如给 Player 类加了个字段），旧的存档可能就读不出来了。

## 总结建议

1.  **如果你想要查询功能**（例如管理几百个物品、怪物数据）：选择 **TinyDB**。它是 JSON 的完美升级版。
2.  **如果你只想存简单的状态**（且不想引入新依赖）：选择 **Shelve**。
3.  **如果你追求极致的开发速度**（直接存对象）：选择 **Pickle**（但要注意代码更新后的存档兼容性）。

对于你的 RPG 游戏，**TinyDB** 是一个非常平衡的选择，既保留了 JSON 的可读性，又提供了方便的数据管理功能。
