from textual.screen import Screen
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Input
from textual.containers import Container
from textual import events
import esper
import os

from src.widgets.game_grid import GameGrid
from src.widgets.status_bar import StatusBar
from src.widgets.command_line import CommandLine
from src.utils.map_loader import load_map_from_file
from src.components.base import Position, Renderable, Velocity, Player
from src.components.equipment import Equipment
from src.systems.render import RenderSystem
from src.systems.movement import MovementSystem
from src.widgets.picker import EquipmentPicker
from src.widgets.space_menu import SpaceMenu
from src.widgets.save_load_picker import SaveLoadPicker
from src.data.database import save_manager

class GameScreen(Screen):
    BINDINGS = [
        Binding("h", "move_left", "Left"),
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
        Binding("l", "move_right", "Right"),
        Binding(":", "command_mode", "Command Mode"),
        Binding("space", "open_picker", "Equipment"),
        Binding("escape", "cancel", "Cancel/Normal"),
    ]

    def __init__(self, save_data=None):
        super().__init__()
        self.can_focus = True
        self.save_data = save_data
        
        # Resolve map path
        base_path = os.getcwd()
        map_path = os.path.join(base_path, "assets/maps/factory_01.txt")
        self.game_map = load_map_from_file(map_path)
        
        self.player_entity = None

    def compose(self) -> ComposeResult:
        yield GameGrid()
        yield StatusBar()
        yield CommandLine()

    def on_mount(self):
        self.game_grid = self.query_one(GameGrid)
        self.status_bar = self.query_one(StatusBar)
        self.command_line = self.query_one(CommandLine)
        
        self.status_bar.map_name = "Factory 01"

        # Init ECS
        self._init_entities()
        self._init_systems()
        
        # Start game loop
        self.set_interval(0.05, self.game_loop) # 20 FPS
        
        # Focus the screen to capture key bindings
        self.call_after_refresh(self.focus)

    def _init_entities(self):
        # Find player start pos
        start_x, start_y = 1, 1
        
        if self.save_data:
            start_x, start_y = self.save_data.get("player_pos", (1, 1))
        else:
            for y, row in enumerate(self.game_map.tiles):
                for x, char in enumerate(row):
                    if char == "@":
                        start_x, start_y = x, y
                        break
        
        self.player_entity = esper.create_entity(
            Position(start_x, start_y),
            Renderable("", "bold cyan", z_index=10),
            Velocity(),
            Player(),
            Equipment()
        )
        
        # Equip items
        eq = esper.component_for_entity(self.player_entity, Equipment)
        
        if self.save_data and "equipment" in self.save_data:
            for slot, item_id in self.save_data["equipment"].items():
                eq.equip(slot, item_id)
        else:
            # Equip starting item
            eq.equip("weapon", "diff_blade_01")
        
        # Add a dummy enemy for visual test
        esper.create_entity(
            Position(start_x + 5, start_y + 2),
            Renderable("", "yellow", z_index=5),
            Velocity(),
        )

    def _init_systems(self):
        esper.add_processor(MovementSystem(self.game_map))
        esper.add_processor(RenderSystem(self.game_grid, self.game_map))

    def game_loop(self):
        esper.process()
        
        # Update Status Bar
        if self.player_entity is not None:
            try:
                pos = esper.component_for_entity(self.player_entity, Position)
                self.status_bar.player_pos = (pos.x, pos.y)
            except KeyError:
                pass

    # --- Actions ---

    def on_click(self):
        self.focus()

    def action_move_left(self):
        if self.status_bar.mode == "NORMAL":
            try:
                esper.component_for_entity(self.player_entity, Velocity).dx = -1
            except KeyError:
                pass

    def action_move_right(self):
        if self.status_bar.mode == "NORMAL":
            try:
                esper.component_for_entity(self.player_entity, Velocity).dx = 1
            except KeyError:
                pass
        
    def action_move_up(self):
        if self.status_bar.mode == "NORMAL":
            try:
                esper.component_for_entity(self.player_entity, Velocity).dy = -1
            except KeyError:
                pass
                
    def action_move_down(self):
        if self.status_bar.mode == "NORMAL":
            try:
                esper.component_for_entity(self.player_entity, Velocity).dy = 1
            except KeyError:
                pass

    def action_command_mode(self):
        """Enter Command Mode"""
        self.status_bar.mode = "COMMAND"
        self.command_line.display = True
        self.command_line.value = ":"
        self.command_line.focus()
        self.call_after_refresh(self._set_command_cursor)

    def action_open_picker(self):
        """Open Space Menu"""
        if self.status_bar.mode == "NORMAL":
            try:
                self.app.push_screen(SpaceMenu(), self._handle_space_menu_result)
            except Exception as e:
                import logging
                logging.basicConfig(filename='crash.log', level=logging.ERROR)
                logging.exception("Crash in action_open_picker")
                self.notify(f"Error: {e}", severity="error")

    def _handle_space_menu_result(self, result):
        if result == "equipment":
            self.app.push_screen(EquipmentPicker(self.player_entity))
        elif result == "save_load":
            # Gather current state to pass to picker
            current_state = self._get_current_state()
            self.app.push_screen(SaveLoadPicker(current_state), self._handle_save_load_result)

    def _get_current_state(self):
        pos = esper.component_for_entity(self.player_entity, Position)
        eq = esper.component_for_entity(self.player_entity, Equipment)
        return {
            "map_name": self.status_bar.map_name,
            "player_pos": (pos.x, pos.y),
            "equipment_slots": eq.slots
        }

    def _handle_save_load_result(self, result):
        if not result:
            return
            
        action, data = result
        # "save" and "overwrite" are now handled inside the picker, 
        # but "load" still needs to be handled here because it changes the screen.
        # Wait, if "save" is handled inside, we don't need to do anything here for it.
        # But the picker might return "load".
        
        if action == "load":
            save_data = save_manager.load_save_by_id(data)
            if save_data:
                self.app.load_game(save_data)
            else:
                self.notify("Failed to load save!", severity="error")

    def _set_command_cursor(self):
        self.command_line.cursor_position = len(self.command_line.value)

    def action_cancel(self):
        """Exit current mode to Normal, or clear selection."""
        if self.status_bar.mode != "NORMAL":
            self._exit_command_mode()
        else:
            # In Vim/Helix, Esc in normal mode doesn't quit.
            pass

    # --- Event Handlers ---

    def on_input_submitted(self, message: Input.Submitted):
        """Handle command submission"""
        if message.input == self.command_line:
            command = message.value.strip()
            self._handle_command(command)
            self._exit_command_mode()

    def on_command_line_cancel(self, message: CommandLine.Cancel):
        """Handle Esc in Command Line"""
        self._exit_command_mode()

    def _exit_command_mode(self):
        self.status_bar.mode = "NORMAL"
        self.command_line.display = False
        self.command_line.value = ""
        self.focus() # Return focus to screen

    def _handle_command(self, command: str):
        """Execute the command"""
        cmd = command.strip()
        if cmd == ":q":
            self.app.pop_screen()
        elif cmd == ":w":
            self._save_game()
            self.notify("Game Saved to saves.db")
        elif cmd == ":wq":
            self._save_game()
            self.notify("Game Saved to saves.db")
            self.app.pop_screen()
        elif cmd == ":q!":
             self.app.pop_screen()
        # Add more commands here

    def _save_game(self):
        pos = esper.component_for_entity(self.player_entity, Position)
        eq = esper.component_for_entity(self.player_entity, Equipment)
        
        save_manager.save_game(
            map_name=self.status_bar.map_name,
            player_pos=(pos.x, pos.y),
            equipment_slots=eq.slots
        )
