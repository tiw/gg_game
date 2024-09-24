import pygame
import sys
from queue import PriorityQueue
import math
import random

# 初始化Pygame
pygame.init()

# 设置常量
GRID_SIZE = 20
CELL_SIZE = 30
MARGIN = 50

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 创建窗口
WIDTH = GRID_SIZE * CELL_SIZE + 2 * MARGIN
HEIGHT = GRID_SIZE * CELL_SIZE + 2 * MARGIN
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Search Algorithm Comparison")

# 定义起点和终点
start = (0, 0)
end = (GRID_SIZE-1, GRID_SIZE-1)

def is_valid_move(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and grid[x][y] == 0

def dfs_path_exists(start, end, grid):
    stack = [start]
    visited = set()

    while stack:
        current = stack.pop()
        if current == end:
            return True
        
        if current in visited:
            continue
        
        visited.add(current)
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_pos = (current[0] + dx, current[1] + dy)
            if is_valid_move(next_pos[0], next_pos[1]) and next_pos not in visited:
                stack.append(next_pos)
    
    return False

def create_complex_maze():
    global grid  # 使用全局变量grid
    while True:
        grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # 创建迷宫的主要结构
        for i in range(0, GRID_SIZE, 4):
            for j in range(GRID_SIZE):
                if i > 0:  # 避免封闭左边界
                    grid[i][j] = 1
                if j > 0:  # 避免封闭上边界
                    grid[j][i] = 1
        
        # 随机开洞
        for i in range(0, GRID_SIZE, 4):
            for _ in range(3):  # 每个墙开3个洞
                j = random.randint(1, GRID_SIZE-2)
                grid[i][j] = 0
                grid[j][i] = 0
        
        # 添加一些随机障碍物
        for _ in range(GRID_SIZE * 2):
            x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
            if (x, y) != start and (x, y) != end:
                grid[x][y] = 1
        
        # 确保起点和终点周围是空的
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if 0 <= start[0]+dx < GRID_SIZE and 0 <= start[1]+dy < GRID_SIZE:
                grid[start[0]+dx][start[1]+dy] = 0
            if 0 <= end[0]+dx < GRID_SIZE and 0 <= end[1]+dy < GRID_SIZE:
                grid[end[0]+dx][end[1]+dy] = 0
        
        # 验证是否存在从起点到终点的路径
        if dfs_path_exists(start, end, grid):
            return grid
        
        print("Regenerating maze...")  # 用于调试，可以看到重新生成的次数

# 使用新的迷宫创建函数
grid = create_complex_maze()

# 辅助函数
def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*CELL_SIZE+MARGIN, y*CELL_SIZE+MARGIN, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_node(pos, color):
    x, y = pos
    rect = pygame.Rect(x*CELL_SIZE+MARGIN, y*CELL_SIZE+MARGIN, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

def heuristic(a, b):
    return max(abs(b[0] - a[0]), abs(b[1] - a[1]))  # 切比雪夫距离

# 在主循环中添加绘制障碍物的代码
def draw_obstacles():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x][y] == 1:
                rect = pygame.Rect(x*CELL_SIZE+MARGIN, y*CELL_SIZE+MARGIN, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (100, 100, 100), rect)

def draw_contours(screen, g_score):
    contour_interval = 5  # 等值线间隔
    max_g = max(g_score.values()) if g_score else 1
    
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) in g_score:
                g = g_score[(x, y)]
                contour_value = int(g / contour_interval)
                color_intensity = int(255 * (1 - g / max_g))
                color = (color_intensity, color_intensity, 255)  # 蓝色渐变
                
                rect = pygame.Rect(x*CELL_SIZE+MARGIN, y*CELL_SIZE+MARGIN, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)
                
                if g % contour_interval < 1:  # 绘制等值线
                    pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def dijkstra(draw):
    queue = PriorityQueue()
    queue.put((0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while not queue.empty():
        current = queue.get()[1]

        if current == end:
            break

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_node = (current[0] + dx, current[1] + dy)
            if is_valid_move(next_node[0], next_node[1]):
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost
                    queue.put((priority, next_node))
                    came_from[next_node] = current
                    draw(next_node, BLUE)
        
        draw_contours(screen, cost_so_far)
        pygame.display.flip()

    return came_from, cost_so_far

def greedy(draw):
    queue = PriorityQueue()
    queue.put((heuristic(start, end), start))
    came_from = {}
    visited = set()
    g_score = {start: 0}

    while not queue.empty():
        current = queue.get()[1]

        if current == end:
            break

        if current in visited:
            continue

        visited.add(current)

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_node = (current[0] + dx, current[1] + dy)
            if is_valid_move(next_node[0], next_node[1]) and next_node not in visited:
                g_score[next_node] = g_score[current] + 1
                priority = heuristic(next_node, end)
                queue.put((priority, next_node))
                came_from[next_node] = current
                draw(next_node, GREEN)
        
        draw_contours(screen, g_score)
        pygame.display.flip()

    return came_from, g_score

def astar(draw):
    queue = PriorityQueue()
    queue.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while not queue.empty():
        current = queue.get()[1]

        if current == end:
            break

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if is_valid_move(neighbor[0], neighbor[1]):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end)
                    queue.put((f_score[neighbor], neighbor))
                    draw(neighbor, RED)
        
        draw_contours(screen, g_score)
        pygame.display.flip()

    return came_from, g_score

def weighted_astar(draw, weight=1.2):
    queue = PriorityQueue()
    queue.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: weight * heuristic(start, end)}

    while not queue.empty():
        current = queue.get()[1]

        if current == end:
            break

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if is_valid_move(neighbor[0], neighbor[1]):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + weight * heuristic(neighbor, end)
                    queue.put((f_score[neighbor], neighbor))
                    draw(neighbor, (255, 165, 0))  # 橙色
        
        draw_contours(screen, g_score)
        pygame.display.flip()

    return came_from, g_score

def main():
    clock = pygame.time.Clock()
    
    algorithms = [
        ("Dijkstra", dijkstra, BLUE),
        ("Greedy", greedy, GREEN),
        ("A*", astar, RED),
        ("Weighted A*", weighted_astar, (255, 165, 0))
    ]

    for name, algo, color in algorithms:
        screen.fill(BLACK)
        draw_grid()
        draw_obstacles()
        draw_node(start, YELLOW)
        draw_node(end, YELLOW)
        pygame.display.flip()

        came_from, g_score = algo(lambda pos, c: (draw_node(pos, c), pygame.display.flip(), clock.tick(60)))

        # 绘制路径
        if end in came_from:
            current = end
            while current != start:
                current = came_from[current]
                if current != start:
                    draw_node(current, YELLOW)
                pygame.display.flip()
                clock.tick(60)

        # 显示算法名称和等待用户输入
        font = pygame.font.Font(None, 36)
        text = font.render(f"{name} search complete. Press any key to continue.", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 40))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
            clock.tick(30)

    # 所有算法完成后
    screen.fill(BLACK)
    text = font.render("All searches complete. Press any key to exit.", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(30)

if __name__ == "__main__":
    main()
    pygame.quit()
