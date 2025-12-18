"""
用户认证系统
处理用户注册、登录、密码验证等
"""
import hashlib
import secrets
from typing import Optional

from src.data.database import Database, get_database
from src.data.models import UserSession


class AuthSystem:
    """用户认证系统"""
    
    def __init__(self, db: Database | None = None):
        self.db = db or get_database()
        self._current_session: UserSession | None = None
    
    @property
    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self._current_session is not None
    
    @property
    def current_user(self) -> UserSession | None:
        """当前登录的用户会话"""
        return self._current_session
    
    @staticmethod
    def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
        """
        对密码进行哈希处理
        
        Returns:
            (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用 SHA-256 + salt
        hash_input = f"{salt}{password}".encode('utf-8')
        password_hash = hashlib.sha256(hash_input).hexdigest()
        
        # 存储格式: salt$hash
        return f"{salt}${password_hash}", salt
    
    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        """验证密码"""
        try:
            salt, hash_value = stored_hash.split('$', 1)
            computed_hash, _ = AuthSystem._hash_password(password, salt)
            return computed_hash == stored_hash
        except ValueError:
            return False
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        注册新用户
        
        Returns:
            (success, message)
        """
        # 验证用户名
        if not username or len(username) < 2:
            return False, "用户名至少需要2个字符"
        
        if len(username) > 20:
            return False, "用户名不能超过20个字符"
        
        if not username.isalnum() and '_' not in username:
            return False, "用户名只能包含字母、数字和下划线"
        
        # 验证密码
        if not password or len(password) < 4:
            return False, "密码至少需要4个字符"
        
        # 检查用户是否已存在
        existing = self.db.get_user_by_username(username)
        if existing:
            return False, f"用户名 '{username}' 已被使用"
        
        # 创建用户
        password_hash, _ = self._hash_password(password)
        user_id = self.db.create_user(username, password_hash)
        
        if user_id:
            return True, f"用户 '{username}' 注册成功"
        else:
            return False, "注册失败，请重试"
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        用户登录
        
        Returns:
            (success, message)
        """
        if self.is_logged_in:
            return False, f"已经以 '{self._current_session.username}' 身份登录，请先登出"
        
        # 获取用户
        user = self.db.get_user_by_username(username)
        if not user:
            return False, "用户名或密码错误"
        
        # 验证密码
        if not self._verify_password(password, user['password_hash']):
            return False, "用户名或密码错误"
        
        # 更新登录时间
        self.db.update_user_login(user['id'])
        
        # 创建会话
        self._current_session = UserSession(
            user_id=user['id'],
            username=user['username'],
            current_path=user['current_path'] or "/"
        )
        
        return True, f"欢迎回来, {username}!"
    
    def logout(self) -> tuple[bool, str]:
        """用户登出"""
        if not self.is_logged_in:
            return False, "当前未登录"
        
        username = self._current_session.username
        
        # 保存当前路径
        self.db.update_user_path(
            self._current_session.user_id,
            self._current_session.current_path
        )
        
        self._current_session = None
        return True, f"再见, {username}"
    
    def update_current_path(self, path: str, node_id: int | None = None) -> None:
        """更新当前会话的路径"""
        if self._current_session:
            self._current_session.current_path = path
            self._current_session.current_node_id = node_id
