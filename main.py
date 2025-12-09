"""算界旅人 - 游戏入口。"""

import asyncio
import sys

import pygame

from src.core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.menu.screens import MainMenuScreen, SaveMenuScreen
from src.scenes import GameScene


async def main():
    """主函数。"""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("算界旅人")
    clock = pygame.time.Clock()

    state = "menu"
    selected_slot = 1

    while True:
        if state == "menu":
            menu = MainMenuScreen(screen)
            result = menu.run()

            if result == "new":
                state = "save_menu_new"
            elif result == "load_menu":
                state = "load_menu"
            elif result == "quit":
                break

        elif state == "save_menu_new":
            save_menu = SaveMenuScreen(screen, mode="save")
            result = save_menu.run()

            if result is None:
                state = "menu"
            elif result.get("action") == "save":
                selected_slot = result["slot"]
                state = "game_new"

        elif state == "load_menu":
            save_menu = SaveMenuScreen(screen, mode="load")
            result = save_menu.run()

            if result is None:
                state = "menu"
            elif result.get("action") == "load":
                selected_slot = result["slot"]
                state = "game_continue"

        elif state == "game_new":
            scene = GameScene(is_new_game=True, slot=selected_slot)
            result = scene.run(screen, clock)

            if result == "main_menu":
                state = "menu"
            else:
                break

        elif state == "game_continue":
            scene = GameScene(is_new_game=False, slot=selected_slot)
            result = scene.run(screen, clock)

            if result == "main_menu":
                state = "menu"
            else:
                break

        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
