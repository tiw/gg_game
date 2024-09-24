import pygame
import os
from map_generator import MapGenerator
from map_generator import LevelLoader

class SokobanGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.player = Actor(0, 0)
        self.theme = Theme()
        self.cell_size = 50
        self.level_loader = LevelLoader()
        self.current_level = 1
        
        # 加载支持中文的字体
        # font_path = os.path.join("fonts", "NotoSansSC-Regular.otf")
        self.font = pygame.font.SysFont("stheitisc", 36)
        if self.font is None:
            print("字体加载失败")
        else:
            print("字体加载成功")
        # self.font = pygame.font.Font(font_path, 36)

    def show_menu(self):
        available_levels = self.level_loader.get_available_levels()
        selected_index = 0

        while True:
            self.screen.fill((255, 255, 255))
            # title = self.font.render("选择关卡", True, (0, 0, 0))
            title = self.font.render("选择关卡".encode('utf-8').decode('utf-8'), True, (0, 0, 0))
            self.screen.blit(title, (350, 50))

            for i, level in enumerate(available_levels):
                color = (255, 0, 0) if i == selected_index else (0, 0, 0)
                text = self.font.render(f"关卡 {level}", True, color)
                self.screen.blit(text, (350, 150 + i * 50))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(available_levels)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(available_levels)
                    elif event.key == pygame.K_RETURN:
                        return available_levels[selected_index]

            self.clock.tick(30)

    def load_level(self, level_number):
        level_data = self.level_loader.load_level(level_number)
        self.state.load_level(level_data)
        if self.state.player_pos:
            self.player.x, self.player.y = self.state.player_pos
        else:
            raise ValueError("无法在关卡中找到玩家起始位置")

    def run(self):
        while True:
            selected_level = self.show_menu()
            if selected_level is None:
                break
            
            self.current_level = selected_level
            self.load_level(self.current_level)

            running = True
            while running:
                running = self.handle_events()
                if self.update():
                    self.show_congratulations()
                    break
                self.draw()
                self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                moved = False
                if event.key == pygame.K_UP:
                    moved = Action.move((0, -1), self.state)
                elif event.key == pygame.K_DOWN:
                    moved = Action.move((0, 1), self.state)
                elif event.key == pygame.K_LEFT:
                    moved = Action.move((-1, 0), self.state)
                elif event.key == pygame.K_RIGHT:
                    moved = Action.move((1, 0), self.state)
                
                if moved:
                    self.player.x, self.player.y = self.state.player_pos
        return True

    def update(self):
        if self.state.is_completed():
            return True
        return False

    def show_congratulations(self):
        self.screen.fill((255, 255, 255))
        congrats_text = self.font.render("祝贺你完成了这关！", True, (0, 0, 0))
        self.screen.blit(congrats_text, (300, 250))
        pygame.display.flip()
        pygame.time.wait(2000)  # 等待 2 秒

    def draw(self):
        self.screen.fill((255, 255, 255))
        for y, row in enumerate(self.state.level):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                if cell == '#':
                    pygame.draw.rect(self.screen, self.theme.wall_color, rect)
                elif (x, y) in self.state.targets:
                    pygame.draw.rect(self.screen, self.theme.target_color, rect, 2)
        
        for box in self.state.boxes:
            rect = pygame.Rect(box[0] * self.cell_size, box[1] * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, self.theme.box_color, rect)
        
        player_rect = pygame.Rect(self.player.x * self.cell_size, self.player.y * self.cell_size, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, self.theme.player_color, player_rect)
        
        pygame.display.flip()

class GameState:
    def __init__(self):
        self.level = None
        self.player_pos = None
        self.boxes = []
        self.targets = []

    def load_level(self, level_data):
        self.level = [list(row) for row in level_data]  # 将每一行转换为可变列表
        self.boxes = []
        self.targets = []
        for y, row in enumerate(self.level):
            for x, cell in enumerate(row):
                if cell == '@':
                    self.player_pos = (x, y)
                    self.level[y][x] = ' '  # 将玩家位置替换为空格
                elif cell == '$':
                    self.boxes.append((x, y))
                elif cell == '.':
                    self.targets.append((x, y))
                elif cell == '*':
                    self.boxes.append((x, y))
                    self.targets.append((x, y))
                    self.level[y][x] = '.'  # 将箱子在目标点上的位置替换为目标点

    def is_completed(self):
        return all(box in self.targets for box in self.boxes)

class Action:
    @staticmethod
    def move(direction, game_state):
        dx, dy = direction
        px, py = game_state.player_pos
        new_x, new_y = px + dx, py + dy
        
        if game_state.level[new_y][new_x] == '#':
            return False  # 撞墙，不移动

        if (new_x, new_y) in game_state.boxes:
            new_box_x, new_box_y = new_x + dx, new_y + dy
            if game_state.level[new_box_y][new_box_x] != '#' and (new_box_x, new_box_y) not in game_state.boxes:
                # 推箱子
                game_state.boxes.remove((new_x, new_y))
                game_state.boxes.append((new_box_x, new_box_y))
            else:
                return False  # 箱子无法移动，玩家也不移动

        game_state.player_pos = (new_x, new_y)
        return True  # 移动成功

    @staticmethod
    def push(direction, game_state):
        # 在这个简化版本中，我们不需要单独的推箱子逻辑
        pass

class Actor:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Theme:
    def __init__(self):
        self.wall_color = (100, 100, 100)
        self.floor_color = (200, 200, 200)
        self.player_color = (0, 0, 255)
        self.box_color = (150, 75, 0)
        self.target_color = (255, 0, 0)

    def load_custom_theme(self, theme_data):
        # 从theme_data加载自定义主题
        pass

if __name__ == "__main__":
    game = SokobanGame()
    game.run()
