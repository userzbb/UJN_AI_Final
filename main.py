import pygame
import sys
import asyncio
from storage import save_game, load_game

# 初始化 Pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My RPG Game")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 128, 255)

# 玩家设置
player_size = 40
# 初始位置
default_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
# 尝试加载存档，如果没有则使用默认位置
saved_data = load_game("save.json", {"pos": default_pos})
player_pos = saved_data["pos"]

player_speed = 5

async def main():
    # 游戏主循环
    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 退出前自动保存
                save_game({"pos": player_pos}, "save.json")
                running = False
            
            # 按 'S' 键手动保存
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game({"pos": player_pos}, "save.json")
                    print("Game Saved!")

        # 2. 获取按键输入
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            player_pos[0] += player_speed
        if keys[pygame.K_UP]:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            player_pos[1] += player_speed

        # 3. 绘制
        screen.fill(BLACK)  # 清屏
        
        # 绘制玩家 (暂时用矩形代替)
        pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0], player_pos[1], player_size, player_size))
        
        # 绘制提示文字
        font = pygame.font.SysFont(None, 24)
        img = font.render('Press S to Save', True, WHITE)
        screen.blit(img, (20, 20))

        # 刷新屏幕
        pygame.display.flip()

        # 控制帧率
        clock.tick(60)
        
        # 关键：交出控制权给浏览器，否则网页会卡死
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
