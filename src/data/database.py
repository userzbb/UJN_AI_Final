"""
数据库管理模块
SQLite 数据库封装，管理用户和虚拟文件系统
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Generator
from datetime import datetime


class Database:
    """SQLite 数据库封装类"""
    
    def __init__(self, db_path: str | Path = "save/game.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
    
    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 允许通过列名访问
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_tables(self) -> None:
        """初始化数据库表"""
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    current_path TEXT DEFAULT '/'
                )
            """)
            
            # 虚拟文件系统表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vfs_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    parent_id INTEGER,
                    name TEXT NOT NULL,
                    is_directory BOOLEAN DEFAULT FALSE,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_id) REFERENCES vfs_nodes(id) ON DELETE CASCADE,
                    UNIQUE(user_id, parent_id, name)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_vfs_user_parent 
                ON vfs_nodes(user_id, parent_id)
            """)
    
    # ==================== 用户操作 ====================
    
    def create_user(self, username: str, password_hash: str) -> int | None:
        """
        创建新用户
        
        Returns:
            用户ID，如果用户名已存在则返回 None
        """
        try:
            with self.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        """通过用户名获取用户信息"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """通过ID获取用户信息"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user_login(self, user_id: int) -> None:
        """更新用户最后登录时间"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user_id)
            )
    
    def update_user_path(self, user_id: int, path: str) -> None:
        """更新用户当前路径"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET current_path = ? WHERE id = ?",
                (path, user_id)
            )
    
    # ==================== 虚拟文件系统操作 ====================
    
    def create_vfs_node(
        self,
        user_id: int,
        parent_id: int | None,
        name: str,
        is_directory: bool = False,
        content: str | None = None
    ) -> int | None:
        """
        创建虚拟文件系统节点
        
        Returns:
            节点ID，如果已存在同名节点则返回 None
        """
        try:
            with self.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO vfs_nodes 
                       (user_id, parent_id, name, is_directory, content)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, parent_id, name, is_directory, content)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_vfs_node(self, node_id: int) -> dict[str, Any] | None:
        """获取节点信息"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM vfs_nodes WHERE id = ?",
                (node_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_vfs_node_by_path(
        self,
        user_id: int,
        parent_id: int | None,
        name: str
    ) -> dict[str, Any] | None:
        """通过父节点ID和名称获取节点"""
        with self.connection() as conn:
            cursor = conn.cursor()
            if parent_id is None:
                cursor.execute(
                    """SELECT * FROM vfs_nodes 
                       WHERE user_id = ? AND parent_id IS NULL AND name = ?""",
                    (user_id, name)
                )
            else:
                cursor.execute(
                    """SELECT * FROM vfs_nodes 
                       WHERE user_id = ? AND parent_id = ? AND name = ?""",
                    (user_id, parent_id, name)
                )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_vfs_children(
        self,
        user_id: int,
        parent_id: int | None
    ) -> list[dict[str, Any]]:
        """获取目录下的所有子节点"""
        with self.connection() as conn:
            cursor = conn.cursor()
            if parent_id is None:
                cursor.execute(
                    """SELECT * FROM vfs_nodes 
                       WHERE user_id = ? AND parent_id IS NULL
                       ORDER BY is_directory DESC, name ASC""",
                    (user_id,)
                )
            else:
                cursor.execute(
                    """SELECT * FROM vfs_nodes 
                       WHERE user_id = ? AND parent_id = ?
                       ORDER BY is_directory DESC, name ASC""",
                    (user_id, parent_id)
                )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_vfs_node_content(self, node_id: int, content: str) -> bool:
        """更新文件内容"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE vfs_nodes 
                   SET content = ?, updated_at = ? 
                   WHERE id = ? AND is_directory = FALSE""",
                (content, datetime.now(), node_id)
            )
            return cursor.rowcount > 0
    
    def rename_vfs_node(self, node_id: int, new_name: str) -> bool:
        """重命名节点"""
        try:
            with self.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE vfs_nodes 
                       SET name = ?, updated_at = ? 
                       WHERE id = ?""",
                    (new_name, datetime.now(), node_id)
                )
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    def delete_vfs_node(self, node_id: int) -> bool:
        """删除节点（级联删除子节点）"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM vfs_nodes WHERE id = ?",
                (node_id,)
            )
            return cursor.rowcount > 0
    
    def get_user_root_nodes(self, user_id: int) -> list[dict[str, Any]]:
        """获取用户的根目录节点"""
        return self.get_vfs_children(user_id, None)


# 全局数据库实例
_db_instance: Database | None = None


def get_database(db_path: str | Path = "save/game.db") -> Database:
    """获取数据库单例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance
