"""
《算界旅人》主应用入口
Textual TUI 游戏应用 - 集成用户系统和虚拟文件系统
"""
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual import on

from src.widgets.terminal import Terminal
from src.systems.auth import AuthSystem
from src.systems.filesystem import VirtualFileSystem
from src.data.database import get_database


class TerminalApp(App):
    """终端模拟器应用"""
    
    CSS_PATH = "../assets/tcss/terminal.tcss"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "退出", show=True),
        Binding("ctrl+l", "clear", "清屏", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.auth = AuthSystem(self.db)
        self.vfs: VirtualFileSystem | None = None
    
    def compose(self) -> ComposeResult:
        yield Terminal(id="main-terminal")
    
    def on_mount(self) -> None:
        """应用挂载时的初始化"""
        terminal = self.query_one("#main-terminal", Terminal)
        terminal.write_info("═══════════════════════════════════════")
        terminal.write_info("       欢迎来到 [bold]算界[/bold] - 计算之域")
        terminal.write_info("═══════════════════════════════════════")
        terminal.write_line("")
        terminal.write_line("在这里，一切皆可计算...")
        terminal.write_line("")
        terminal.write_line("请输入 [cyan]register <用户名> <密码>[/cyan] 注册新账户")
        terminal.write_line("或输入 [cyan]login <用户名> <密码>[/cyan] 登录已有账户")
        terminal.write_line("输入 [cyan]help[/cyan] 查看所有可用命令")
        terminal.write_line("")
    
    @on(Terminal.CommandExecuted)
    def handle_command(self, event: Terminal.CommandExecuted) -> None:
        """处理终端命令"""
        terminal = event.terminal
        command = event.command.strip()
        parts = command.split()
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # 命令路由
        match cmd:
            # === 基础命令 ===
            case "help":
                self._show_help(terminal)
            case "clear" | "cls":
                terminal.clear()
            case "exit" | "quit":
                self.exit()
            case "echo":
                terminal.write_line(" ".join(args))
            
            # === 用户命令 ===
            case "register":
                self._handle_register(terminal, args)
            case "login":
                self._handle_login(terminal, args)
            case "logout":
                self._handle_logout(terminal)
            case "whoami":
                self._handle_whoami(terminal)
            
            # === 文件系统命令 (需要登录) ===
            case "pwd":
                self._handle_pwd(terminal)
            case "cd":
                self._handle_cd(terminal, args)
            case "ls":
                self._handle_ls(terminal, args)
            case "mkdir":
                self._handle_mkdir(terminal, args)
            case "touch":
                self._handle_touch(terminal, args)
            case "cat":
                self._handle_cat(terminal, args)
            case "rm":
                self._handle_rm(terminal, args)
            case "mv":
                self._handle_mv(terminal, args)
            case "write":
                self._handle_write(terminal, args)
            case "tree":
                self._handle_tree(terminal)
            
            case _:
                terminal.write_error(f"未知命令: {cmd}")
                terminal.write_line("输入 [cyan]help[/cyan] 查看可用命令")
    
    def _require_login(self, terminal: Terminal) -> bool:
        """检查是否已登录"""
        if not self.auth.is_logged_in:
            terminal.write_error("请先登录")
            terminal.write_line("使用 [cyan]login <用户名> <密码>[/cyan] 登录")
            return False
        return True
    
    # ==================== 帮助命令 ====================
    
    def _show_help(self, terminal: Terminal) -> None:
        """显示帮助信息"""
        terminal.write_line("")
        terminal.write_info("═══ 用户命令 ═══")
        terminal.write_line("  [cyan]register <用户名> <密码>[/cyan]  - 注册新账户")
        terminal.write_line("  [cyan]login <用户名> <密码>[/cyan]     - 登录")
        terminal.write_line("  [cyan]logout[/cyan]                    - 登出")
        terminal.write_line("  [cyan]whoami[/cyan]                    - 显示当前用户")
        terminal.write_line("")
        terminal.write_info("═══ 文件命令 (需登录) ═══")
        terminal.write_line("  [cyan]pwd[/cyan]                       - 显示当前路径")
        terminal.write_line("  [cyan]cd <路径>[/cyan]                 - 切换目录")
        terminal.write_line("  [cyan]ls [路径][/cyan]                 - 列出目录内容")
        terminal.write_line("  [cyan]mkdir <名称>[/cyan]              - 创建目录")
        terminal.write_line("  [cyan]touch <文件名>[/cyan]            - 创建空文件")
        terminal.write_line("  [cyan]cat <文件名>[/cyan]              - 查看文件内容")
        terminal.write_line("  [cyan]write <文件名> <内容>[/cyan]     - 写入文件")
        terminal.write_line("  [cyan]rm [-r] <名称>[/cyan]            - 删除文件/目录")
        terminal.write_line("  [cyan]mv <源> <目标>[/cyan]            - 重命名")
        terminal.write_line("  [cyan]tree[/cyan]                      - 显示目录树")
        terminal.write_line("")
        terminal.write_info("═══ 系统命令 ═══")
        terminal.write_line("  [cyan]clear[/cyan]                     - 清空终端")
        terminal.write_line("  [cyan]echo <文本>[/cyan]               - 输出文本")
        terminal.write_line("  [cyan]exit[/cyan]                      - 退出程序")
        terminal.write_line("")
    
    # ==================== 用户命令处理 ====================
    
    def _handle_register(self, terminal: Terminal, args: list[str]) -> None:
        """处理注册命令"""
        if len(args) < 2:
            terminal.write_error("用法: register <用户名> <密码>")
            return
        
        username, password = args[0], args[1]
        success, message = self.auth.register(username, password)
        
        if success:
            terminal.write_success(message)
            terminal.write_line("现在可以使用 [cyan]login[/cyan] 命令登录")
        else:
            terminal.write_error(message)
    
    def _handle_login(self, terminal: Terminal, args: list[str]) -> None:
        """处理登录命令"""
        if len(args) < 2:
            terminal.write_error("用法: login <用户名> <密码>")
            return
        
        username, password = args[0], args[1]
        success, message = self.auth.login(username, password)
        
        if success:
            terminal.write_success(message)
            terminal.write_line("")
            
            # 初始化虚拟文件系统
            user = self.auth.current_user
            self.vfs = VirtualFileSystem(user.user_id, self.db)
            
            # 检查是否是新用户（没有任何文件）
            root_nodes = self.db.get_user_root_nodes(user.user_id)
            if not root_nodes:
                self.vfs.init_default_structure()
                terminal.write_info("已为你创建默认目录结构")
            
            # 恢复上次的路径
            if user.current_path != "/":
                result = self.vfs.cd(user.current_path)
                if not result.success:
                    self.vfs.cd("/")
            
            # 更新终端提示符
            terminal.login(username, "算界")
            terminal.set_cwd(self.vfs.cwd)
            
            terminal.write_line("")
            terminal.write_info("你已进入 [bold]算界[/bold]")
            terminal.write_line("输入 [cyan]ls[/cyan] 查看你的文件")
        else:
            terminal.write_error(message)
    
    def _handle_logout(self, terminal: Terminal) -> None:
        """处理登出命令"""
        if not self.auth.is_logged_in:
            terminal.write_error("当前未登录")
            return
        
        # 保存当前路径
        if self.vfs:
            self.auth.update_current_path(self.vfs.cwd)
        
        success, message = self.auth.logout()
        
        if success:
            terminal.write_info(message)
            terminal.logout()
            self.vfs = None
        else:
            terminal.write_error(message)
    
    def _handle_whoami(self, terminal: Terminal) -> None:
        """显示当前用户"""
        if self.auth.is_logged_in:
            terminal.write_line(self.auth.current_user.username)
        else:
            terminal.write_error("未登录")
    
    # ==================== 文件系统命令处理 ====================
    
    def _handle_pwd(self, terminal: Terminal) -> None:
        """显示当前路径"""
        if not self._require_login(terminal):
            return
        terminal.write_line(self.vfs.pwd())
    
    def _handle_cd(self, terminal: Terminal, args: list[str]) -> None:
        """切换目录"""
        if not self._require_login(terminal):
            return
        
        path = args[0] if args else ""
        result = self.vfs.cd(path)
        
        if result.success:
            terminal.set_cwd(self.vfs.cwd)
            # 更新会话路径
            self.auth.update_current_path(self.vfs.cwd, self.vfs.current_node_id)
        else:
            terminal.write_error(result.message)
    
    def _handle_ls(self, terminal: Terminal, args: list[str]) -> None:
        """列出目录内容"""
        if not self._require_login(terminal):
            return
        
        path = args[0] if args else ""
        result = self.vfs.ls(path)
        
        if not result.success:
            terminal.write_error(result.message)
            return
        
        if not result.data:
            terminal.write_line("[dim](空目录)[/dim]")
            return
        
        for item in result.data:
            if item['is_directory']:
                terminal.write_line(f"[blue]{item['name']}/[/blue]")
            else:
                terminal.write_line(item['name'])
    
    def _handle_mkdir(self, terminal: Terminal, args: list[str]) -> None:
        """创建目录"""
        if not self._require_login(terminal):
            return
        
        if not args:
            terminal.write_error("用法: mkdir <目录名>")
            return
        
        result = self.vfs.mkdir(args[0])
        if result.success:
            terminal.write_success(result.message)
        else:
            terminal.write_error(result.message)
    
    def _handle_touch(self, terminal: Terminal, args: list[str]) -> None:
        """创建文件"""
        if not self._require_login(terminal):
            return
        
        if not args:
            terminal.write_error("用法: touch <文件名>")
            return
        
        result = self.vfs.touch(args[0])
        if result.success:
            terminal.write_success(result.message)
        else:
            terminal.write_error(result.message)
    
    def _handle_cat(self, terminal: Terminal, args: list[str]) -> None:
        """查看文件内容"""
        if not self._require_login(terminal):
            return
        
        if not args:
            terminal.write_error("用法: cat <文件名>")
            return
        
        result = self.vfs.cat(args[0])
        if result.success:
            content = result.data or "(空文件)"
            for line in content.split("\n"):
                terminal.write_line(line)
        else:
            terminal.write_error(result.message)
    
    def _handle_write(self, terminal: Terminal, args: list[str]) -> None:
        """写入文件内容"""
        if not self._require_login(terminal):
            return
        
        if len(args) < 2:
            terminal.write_error("用法: write <文件名> <内容>")
            return
        
        filename = args[0]
        content = " ".join(args[1:])
        
        result = self.vfs.write(filename, content)
        if result.success:
            terminal.write_success(result.message)
        else:
            terminal.write_error(result.message)
    
    def _handle_rm(self, terminal: Terminal, args: list[str]) -> None:
        """删除文件或目录"""
        if not self._require_login(terminal):
            return
        
        if not args:
            terminal.write_error("用法: rm [-r] <名称>")
            return
        
        recursive = False
        target = args[0]
        
        if args[0] == "-r":
            recursive = True
            if len(args) < 2:
                terminal.write_error("用法: rm -r <目录名>")
                return
            target = args[1]
        
        if recursive:
            result = self.vfs.rm_recursive(target)
        else:
            result = self.vfs.rm(target)
        
        if result.success:
            terminal.write_success(result.message)
        else:
            terminal.write_error(result.message)
    
    def _handle_mv(self, terminal: Terminal, args: list[str]) -> None:
        """移动/重命名"""
        if not self._require_login(terminal):
            return
        
        if len(args) < 2:
            terminal.write_error("用法: mv <源> <目标>")
            return
        
        result = self.vfs.mv(args[0], args[1])
        if result.success:
            terminal.write_success(result.message)
        else:
            terminal.write_error(result.message)
    
    def _handle_tree(self, terminal: Terminal) -> None:
        """显示目录树"""
        if not self._require_login(terminal):
            return
        
        terminal.write_line(f"[bold]{self.vfs.cwd}[/bold]")
        result = self.vfs.tree()
        if result.success and result.data:
            for line in result.data:
                terminal.write_line(line)
        elif not result.data:
            terminal.write_line("[dim](空目录)[/dim]")
    
    def action_clear(self) -> None:
        """清屏动作"""
        terminal = self.query_one("#main-terminal", Terminal)
        terminal.clear()


def run_app() -> None:
    """运行应用"""
    app = TerminalApp()
    app.run()


if __name__ == "__main__":
    run_app()
