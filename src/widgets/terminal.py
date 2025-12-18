"""
终端模拟器组件 - 类似 Linux 终端的交互界面
"""
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import ScrollableContainer, Vertical
from textual.message import Message
from textual import on
from textual.reactive import reactive
from rich.text import Text


class TerminalLine(Static):
    """终端中的单行输出"""
    
    DEFAULT_CSS = """
    TerminalLine {
        height: auto;
        width: 100%;
        padding: 0;
        margin: 0;
    }
    """


class TerminalPrompt(Widget):
    """终端提示符和输入区域"""
    
    DEFAULT_CSS = """
    TerminalPrompt {
        layout: horizontal;
        height: auto;
        width: 100%;
    }
    
    TerminalPrompt .prompt-text {
        width: auto;
        height: auto;
        padding: 0;
        margin: 0;
        color: $success;
    }
    
    TerminalPrompt .prompt-input {
        width: 1fr;
        height: auto;
        border: none;
        padding: 0;
        margin: 0;
        background: transparent;
    }
    
    TerminalPrompt .prompt-input:focus {
        border: none;
    }
    """
    
    # 提示符文本 (响应式属性)
    prompt = reactive("$ ")
    
    class CommandSubmitted(Message):
        """命令提交消息"""
        def __init__(self, command: str) -> None:
            self.command = command
            super().__init__()
    
    def __init__(
        self,
        prompt: str = "$ ",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.prompt = prompt
    
    def compose(self) -> ComposeResult:
        yield Static(self.prompt, classes="prompt-text")
        yield Input(placeholder="", classes="prompt-input")
    
    def watch_prompt(self, new_prompt: str) -> None:
        """当提示符改变时更新显示"""
        try:
            prompt_widget = self.query_one(".prompt-text", Static)
            prompt_widget.update(new_prompt)
        except Exception:
            pass
    
    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交"""
        event.stop()
        command = event.value.strip()
        event.input.value = ""
        self.post_message(self.CommandSubmitted(command))
    
    def focus_input(self) -> None:
        """聚焦到输入框"""
        try:
            input_widget = self.query_one(".prompt-input", Input)
            input_widget.focus()
        except Exception:
            pass


class Terminal(Widget):
    """
    终端模拟器 Widget
    
    支持:
    - 显示命令历史
    - 自定义提示符 (如 $ 或 user@host:path$ )
    - 命令输入和处理
    - 滚动历史记录
    """
    
    DEFAULT_CSS = """
    Terminal {
        width: 100%;
        height: 100%;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }
    
    Terminal #terminal-history {
        width: 100%;
        height: 1fr;
        scrollbar-size: 1 1;
    }
    
    Terminal .output-line {
        color: $text;
    }
    
    Terminal .output-line.error {
        color: $error;
    }
    
    Terminal .output-line.success {
        color: $success;
    }
    
    Terminal .output-line.info {
        color: $primary;
    }
    
    Terminal .command-echo {
        color: $text-muted;
    }
    """
    
    # 当前工作目录
    cwd = reactive("/")
    # 用户名
    username = reactive("")
    # 主机名
    hostname = reactive("")
    # 是否显示完整提示符 (登录后)
    logged_in = reactive(False)
    
    class CommandExecuted(Message):
        """命令执行消息 - 供外部处理"""
        def __init__(self, command: str, terminal: "Terminal") -> None:
            self.command = command
            self.terminal = terminal
            super().__init__()
    
    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._command_history: list[str] = []
        self._history_index: int = 0
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield ScrollableContainer(id="terminal-history")
            yield TerminalPrompt(prompt=self._get_prompt(), id="terminal-prompt")
    
    def _get_prompt(self) -> str:
        """生成提示符字符串"""
        if not self.logged_in:
            return "$ "
        
        # 登录后显示完整提示符: user@host:path$
        user_part = f"{self.username}@{self.hostname}" if self.username else ""
        if user_part:
            return f"[green]{user_part}[/green]:[cyan]{self.cwd}[/cyan]$ "
        return f"[cyan]{self.cwd}[/cyan]$ "
    
    def _update_prompt(self) -> None:
        """更新提示符显示"""
        try:
            prompt_widget = self.query_one("#terminal-prompt", TerminalPrompt)
            prompt_widget.prompt = self._get_prompt()
        except Exception:
            pass
    
    def watch_cwd(self, new_cwd: str) -> None:
        """监听工作目录变化"""
        self._update_prompt()
    
    def watch_logged_in(self, logged_in: bool) -> None:
        """监听登录状态变化"""
        self._update_prompt()
    
    def watch_username(self, username: str) -> None:
        """监听用户名变化"""
        self._update_prompt()
    
    def watch_hostname(self, hostname: str) -> None:
        """监听主机名变化"""
        self._update_prompt()
    
    def on_mount(self) -> None:
        """挂载时聚焦输入"""
        self.call_after_refresh(self._focus_prompt)
    
    def _focus_prompt(self) -> None:
        """聚焦到提示符输入"""
        try:
            prompt = self.query_one("#terminal-prompt", TerminalPrompt)
            prompt.focus_input()
        except Exception:
            pass
    
    @on(TerminalPrompt.CommandSubmitted)
    def on_command_submitted(self, event: TerminalPrompt.CommandSubmitted) -> None:
        """处理命令提交"""
        event.stop()
        command = event.command
        
        if command:
            # 添加到历史记录
            self._command_history.append(command)
            self._history_index = len(self._command_history)
            
            # 显示输入的命令
            self.write_line(f"{self._get_prompt()}{command}", classes="command-echo")
            
            # 发送命令执行消息
            self.post_message(self.CommandExecuted(command, self))
    
    def write_line(
        self,
        text: str,
        classes: str = "output-line",
        markup: bool = True
    ) -> None:
        """
        向终端写入一行文本
        
        Args:
            text: 要显示的文本
            classes: CSS 类名 (output-line, error, success, info)
            markup: 是否解析 Rich markup
        """
        history = self.query_one("#terminal-history", ScrollableContainer)
        line = TerminalLine(text, classes=classes, markup=markup)
        history.mount(line)
        # 滚动到底部
        history.scroll_end(animate=False)
    
    def write_error(self, text: str) -> None:
        """写入错误信息"""
        self.write_line(f"[red]{text}[/red]", classes="output-line error")
    
    def write_success(self, text: str) -> None:
        """写入成功信息"""
        self.write_line(f"[green]{text}[/green]", classes="output-line success")
    
    def write_info(self, text: str) -> None:
        """写入提示信息"""
        self.write_line(f"[blue]{text}[/blue]", classes="output-line info")
    
    def clear(self) -> None:
        """清空终端历史"""
        history = self.query_one("#terminal-history", ScrollableContainer)
        history.remove_children()
    
    def login(self, username: str, hostname: str = "算界") -> None:
        """
        执行登录，切换到完整提示符模式
        
        Args:
            username: 用户名
            hostname: 主机名
        """
        self.username = username
        self.hostname = hostname
        self.logged_in = True
    
    def logout(self) -> None:
        """登出，切换回简单提示符"""
        self.username = ""
        self.hostname = ""
        self.logged_in = False
    
    def set_cwd(self, path: str) -> None:
        """设置当前工作目录"""
        self.cwd = path
