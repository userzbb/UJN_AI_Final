from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Markdown, Static, ListView, ListItem, Label
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from src.widgets.command_line import CommandLine
import os

from src.data.database import save_manager
from src.widgets.save_load_picker import SaveLoadPicker

class TitleScreen(Screen):
    CSS_PATH = "../../assets/tcss/title.tcss"
    
    BINDINGS = [
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("enter", "select", "Select"),
        Binding(":", "command_mode", "Command Mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Vertical(id="left-pane"):
                yield Static("TimeStack: A Computing History TUI\n时 栈", id="game-title")
                
                # Menu
                yield ListView(
                    ListItem(Label("New Game (开启新游戏)", classes="menu-item"), id="opt-new"),
                    ListItem(Label("Load Game (读取存档)", classes="menu-item"), id="opt-load"),
                    ListItem(Label("Quit (退出)", classes="menu-item"), id="opt-quit"),
                    id="main-menu"
                )
            
            with Vertical(id="right-pane"):
                yield Markdown(id="intro-markdown")
        
        yield CommandLine()
        yield Footer()

    def on_mount(self):
        self.load_intro()
        self.query_one("#main-menu").focus()

    def load_intro(self):
        try:
            with open("assets/docs/intro.md", "r", encoding="utf-8") as f:
                md_content = f.read()
            self.query_one(Markdown).update(md_content)
        except Exception as e:
            self.query_one(Markdown).update(f"Error loading intro: {e}")

    def action_cursor_down(self):
        self.query_one(ListView).action_cursor_down()
        
    def action_cursor_up(self):
        self.query_one(ListView).action_cursor_up()

    def action_select(self):
        # Delegate to ListView's select action, which posts ListView.Selected
        self.query_one(ListView).action_select()

    def on_list_view_selected(self, message: ListView.Selected):
        """Handle mouse click or enter on ListView"""
        self._handle_menu_selection(message.item.id)

    def _handle_menu_selection(self, opt_id):
        if opt_id == "opt-new":
            self.app.start_new_game()
        elif opt_id == "opt-load":
            try:
                self.app.push_screen(SaveLoadPicker(current_state=None), self._handle_load_result)
            except Exception as e:
                import logging
                logging.basicConfig(filename='crash_title.log', level=logging.ERROR)
                logging.exception("Crash in TitleScreen load game")
                self.notify(f"Error: {e}", severity="error")
        elif opt_id == "opt-quit":
            self.app.exit()

    def _handle_load_result(self, result):
        if result and result[0] == "load":
            save_id = result[1]
            save_data = save_manager.load_save_by_id(save_id)
            if save_data:
                self.app.load_game(save_data)
            else:
                self.notify("Failed to load save!", severity="error")

    # --- Command Mode Support ---
    
    def action_command_mode(self):
        self.query_one(CommandLine).display = True
        self.query_one(CommandLine).value = ":"
        self.query_one(CommandLine).focus()
        self.call_after_refresh(self._set_command_cursor)

    def _set_command_cursor(self):
        cmd = self.query_one(CommandLine)
        cmd.cursor_position = len(cmd.value)

    def on_command_line_cancel(self, message: CommandLine.Cancel):
        cmd = self.query_one(CommandLine)
        cmd.display = False
        cmd.value = ""
        self.query_one("#main-menu").focus()

    def on_input_submitted(self, message):
        if message.input == self.query_one(CommandLine):
            cmd = message.value.strip()
            self._handle_command(cmd)
            self.on_command_line_cancel(None)

    def _handle_command(self, command):
        if command == ":new":
            self.app.start_new_game()
        elif command == ":q":
            self.app.exit()
        elif command == ":load":
            self.notify("Save system not implemented yet!")
        else:
            self.notify(f"Unknown command: {command}")
