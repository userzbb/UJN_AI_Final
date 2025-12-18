"""
虚拟文件系统
每个用户拥有独立的文件空间，支持 CRUD 操作
"""
from typing import Optional
from dataclasses import dataclass

from src.data.database import Database, get_database


@dataclass
class FSResult:
    """文件系统操作结果"""
    success: bool
    message: str
    data: any = None


class VirtualFileSystem:
    """
    虚拟文件系统
    
    提供类 Unix 风格的文件操作接口
    每个用户拥有独立的文件树
    """
    
    def __init__(self, user_id: int, db: Database | None = None):
        self.user_id = user_id
        self.db = db or get_database()
        self._current_node_id: int | None = None  # None 表示根目录
        self._current_path: str = "/"
    
    @property
    def cwd(self) -> str:
        """当前工作目录路径"""
        return self._current_path
    
    @property
    def current_node_id(self) -> int | None:
        """当前目录节点ID"""
        return self._current_node_id
    
    def _resolve_path(self, path: str) -> tuple[int | None, str, bool]:
        """
        解析路径，返回节点ID和规范化路径
        
        Returns:
            (node_id, normalized_path, exists)
            node_id: 目标节点ID（None表示根目录）
            normalized_path: 规范化后的路径
            exists: 路径是否存在
        """
        # 处理绝对路径和相对路径
        if path.startswith("/"):
            # 绝对路径
            parts = [p for p in path.split("/") if p]
            current_id = None
            current_path = "/"
        else:
            # 相对路径
            parts = [p for p in path.split("/") if p]
            current_id = self._current_node_id
            current_path = self._current_path.rstrip("/")
        
        # 逐级解析
        for part in parts:
            if part == ".":
                continue
            elif part == "..":
                # 返回上级目录
                if current_id is not None:
                    node = self.db.get_vfs_node(current_id)
                    if node:
                        current_id = node['parent_id']
                        # 更新路径
                        if current_path != "/":
                            current_path = "/".join(current_path.rsplit("/", 1)[:-1]) or "/"
            else:
                # 查找子节点
                node = self.db.get_vfs_node_by_path(self.user_id, current_id, part)
                if node:
                    current_id = node['id']
                    current_path = f"{current_path.rstrip('/')}/{part}"
                else:
                    # 路径不存在
                    target_path = f"{current_path.rstrip('/')}/{part}"
                    return None, target_path, False
        
        return current_id, current_path or "/", True
    
    def cd(self, path: str) -> FSResult:
        """切换目录"""
        if not path:
            # 回到根目录
            self._current_node_id = None
            self._current_path = "/"
            return FSResult(True, "/")
        
        node_id, resolved_path, exists = self._resolve_path(path)
        
        if not exists:
            return FSResult(False, f"目录不存在: {resolved_path}")
        
        # 检查是否是目录
        if node_id is not None:
            node = self.db.get_vfs_node(node_id)
            if node and not node['is_directory']:
                return FSResult(False, f"不是目录: {resolved_path}")
        
        self._current_node_id = node_id
        self._current_path = resolved_path
        return FSResult(True, resolved_path)
    
    def ls(self, path: str = "") -> FSResult:
        """列出目录内容"""
        if path:
            node_id, resolved_path, exists = self._resolve_path(path)
            if not exists:
                return FSResult(False, f"目录不存在: {resolved_path}")
            
            # 检查是否是目录
            if node_id is not None:
                node = self.db.get_vfs_node(node_id)
                if node and not node['is_directory']:
                    # 如果是文件，返回文件信息
                    return FSResult(True, "", [node])
        else:
            node_id = self._current_node_id
        
        children = self.db.get_vfs_children(self.user_id, node_id)
        return FSResult(True, "", children)
    
    def mkdir(self, name: str) -> FSResult:
        """创建目录"""
        if not name or "/" in name:
            return FSResult(False, "无效的目录名")
        
        # 检查是否已存在
        existing = self.db.get_vfs_node_by_path(
            self.user_id, self._current_node_id, name
        )
        if existing:
            return FSResult(False, f"已存在: {name}")
        
        node_id = self.db.create_vfs_node(
            self.user_id,
            self._current_node_id,
            name,
            is_directory=True
        )
        
        if node_id:
            return FSResult(True, f"目录已创建: {name}")
        return FSResult(False, "创建目录失败")
    
    def touch(self, name: str, content: str = "") -> FSResult:
        """创建文件"""
        if not name or "/" in name:
            return FSResult(False, "无效的文件名")
        
        # 检查是否已存在
        existing = self.db.get_vfs_node_by_path(
            self.user_id, self._current_node_id, name
        )
        if existing:
            # 如果存在且是文件，更新内容
            if not existing['is_directory']:
                self.db.update_vfs_node_content(existing['id'], content)
                return FSResult(True, f"文件已更新: {name}")
            return FSResult(False, f"同名目录已存在: {name}")
        
        node_id = self.db.create_vfs_node(
            self.user_id,
            self._current_node_id,
            name,
            is_directory=False,
            content=content
        )
        
        if node_id:
            return FSResult(True, f"文件已创建: {name}")
        return FSResult(False, "创建文件失败")
    
    def cat(self, name: str) -> FSResult:
        """读取文件内容"""
        node_id, resolved_path, exists = self._resolve_path(name)
        
        if not exists:
            return FSResult(False, f"文件不存在: {name}")
        
        if node_id is None:
            return FSResult(False, "无法读取根目录")
        
        node = self.db.get_vfs_node(node_id)
        if not node:
            return FSResult(False, f"文件不存在: {name}")
        
        if node['is_directory']:
            return FSResult(False, f"是目录，不是文件: {name}")
        
        return FSResult(True, "", node['content'] or "")
    
    def write(self, name: str, content: str) -> FSResult:
        """写入文件内容"""
        # 先尝试解析路径
        node_id, resolved_path, exists = self._resolve_path(name)
        
        if exists and node_id is not None:
            node = self.db.get_vfs_node(node_id)
            if node and node['is_directory']:
                return FSResult(False, f"是目录，不是文件: {name}")
            
            # 更新现有文件
            self.db.update_vfs_node_content(node_id, content)
            return FSResult(True, f"文件已更新: {name}")
        
        # 文件不存在，创建新文件
        return self.touch(name, content)
    
    def rm(self, name: str) -> FSResult:
        """删除文件或空目录"""
        node_id, resolved_path, exists = self._resolve_path(name)
        
        if not exists:
            return FSResult(False, f"不存在: {name}")
        
        if node_id is None:
            return FSResult(False, "无法删除根目录")
        
        node = self.db.get_vfs_node(node_id)
        if not node:
            return FSResult(False, f"不存在: {name}")
        
        # 如果是目录，检查是否为空
        if node['is_directory']:
            children = self.db.get_vfs_children(self.user_id, node_id)
            if children:
                return FSResult(False, f"目录不为空: {name} (使用 rm -r 删除)")
        
        if self.db.delete_vfs_node(node_id):
            return FSResult(True, f"已删除: {name}")
        return FSResult(False, "删除失败")
    
    def rm_recursive(self, name: str) -> FSResult:
        """递归删除目录"""
        node_id, resolved_path, exists = self._resolve_path(name)
        
        if not exists:
            return FSResult(False, f"不存在: {name}")
        
        if node_id is None:
            return FSResult(False, "无法删除根目录")
        
        # 递归删除会由数据库的 CASCADE 处理
        if self.db.delete_vfs_node(node_id):
            return FSResult(True, f"已删除: {name}")
        return FSResult(False, "删除失败")
    
    def mv(self, src: str, dst: str) -> FSResult:
        """移动/重命名文件或目录"""
        src_id, src_path, src_exists = self._resolve_path(src)
        
        if not src_exists or src_id is None:
            return FSResult(False, f"源不存在: {src}")
        
        # 简单重命名（同目录下）
        if "/" not in dst:
            if self.db.rename_vfs_node(src_id, dst):
                return FSResult(True, f"已重命名: {src} -> {dst}")
            return FSResult(False, f"目标已存在: {dst}")
        
        return FSResult(False, "暂不支持跨目录移动")
    
    def pwd(self) -> str:
        """返回当前工作目录"""
        return self._current_path
    
    def tree(self, depth: int = 3) -> FSResult:
        """显示目录树结构"""
        lines = []
        self._build_tree(self._current_node_id, "", lines, depth, 0)
        return FSResult(True, "", lines)
    
    def _build_tree(
        self,
        node_id: int | None,
        prefix: str,
        lines: list[str],
        max_depth: int,
        current_depth: int
    ) -> None:
        """递归构建目录树"""
        if current_depth >= max_depth:
            return
        
        children = self.db.get_vfs_children(self.user_id, node_id)
        
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            connector = "└── " if is_last else "├── "
            
            name = child['name']
            if child['is_directory']:
                name = f"[blue]{name}/[/blue]"
            
            lines.append(f"{prefix}{connector}{name}")
            
            if child['is_directory']:
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._build_tree(
                    child['id'],
                    new_prefix,
                    lines,
                    max_depth,
                    current_depth + 1
                )
    
    def init_default_structure(self) -> None:
        """初始化默认目录结构"""
        # 创建默认目录
        default_dirs = ["home", "documents", "downloads", "data"]
        
        for dir_name in default_dirs:
            self.db.create_vfs_node(
                self.user_id,
                None,  # 根目录
                dir_name,
                is_directory=True
            )
        
        # 创建欢迎文件
        self.db.create_vfs_node(
            self.user_id,
            None,
            "README.txt",
            is_directory=False,
            content="欢迎来到算界！\n\n这是你的个人空间，你可以在这里存储文件和数据。\n\n使用 help 命令查看可用操作。"
        )
