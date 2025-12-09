from textual.app import App
from textual.binding import Binding
from src.screens.game_screen import GameScreen
from src.screens.title_screen import TitleScreen
import os

class RealmTravelerApp(App):
    CSS_PATH = os.path.join(os.getcwd(), "assets/tcss/styles.tcss")
    
    BINDINGS = [
        Binding("h", "move_left", "Left"),
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
        Binding("l", "move_right", "Right"),
        Binding(":", "command_mode", "Command Mode"),
        Binding("space", "open_picker", "Equipment"),
    ]

    def on_mount(self):
        self.push_screen(TitleScreen())

    def start_new_game(self):
        self.push_screen(GameScreen())

    def load_game(self, save_data):
        self.push_screen(GameScreen(save_data=save_data))

    def action_move_left(self):
        if isinstance(self.screen, GameScreen):
            self.screen.action_move_left()
            
    def action_move_right(self):
        if isinstance(self.screen, GameScreen):
            self.screen.action_move_right()
            
    def action_move_up(self):
        if isinstance(self.screen, GameScreen):
            self.screen.action_move_up()
            
    def action_move_down(self):
        if isinstance(self.screen, GameScreen):
            self.screen.action_move_down()

    def action_command_mode(self):
        if isinstance(self.screen, GameScreen):
            self.screen.action_command_mode()

    def action_open_picker(self):
        if isinstance(self.screen, GameScreen):
            self.screen.action_open_picker()
