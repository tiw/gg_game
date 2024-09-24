import random
from collections import deque

class MapGenerator:
    def __init__(self):
        self.wall = '#'
        self.floor = ' '
        self.player = '@'
        self.box = '$'
        self.target = '.'
        self.box_on_target = '*'
        self.max_level = 10
        self.generated_maps = {}

    def generate_level(self, difficulty):
        if difficulty < 1 or difficulty > self.max_level:
            raise ValueError(f"难度级别必须在 1 到 {self.max_level} 之间")

        if difficulty not in self.generated_maps:
            width = random.randint(8 + difficulty, 12 + difficulty)
            height = random.randint(8 + difficulty, 12 + difficulty)
            num_boxes = random.randint(1 + difficulty // 2, 2 + difficulty)
            
            while True:
                map_data = self.create_map(width, height, num_boxes, difficulty / 10)
                if self.is_solvable(map_data):
                    self.generated_maps[difficulty] = map_data
                    break

        return self.generated_maps[difficulty]

    def create_map(self, width, height, num_boxes, difficulty):
        map_data = self.create_initial_map(width, height, difficulty)
        player_pos = self.place_element(map_data, self.player)
        self.ensure_connectivity(map_data, player_pos)
        
        for _ in range(num_boxes):
            self.place_element(map_data, self.box)
            self.place_element(map_data, self.target)
        
        return map_data

    def create_initial_map(self, width, height, difficulty):
        map_data = [[self.wall] * width for _ in range(height)]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if random.random() > difficulty * 0.1:
                    map_data[y][x] = self.floor
        return map_data

    def place_element(self, map_data, element):
        height, width = len(map_data), len(map_data[0])
        while True:
            x, y = random.randint(1, width - 2), random.randint(1, height - 2)
            if map_data[y][x] == self.floor:
                map_data[y][x] = element
                return (x, y)

    def ensure_connectivity(self, map_data, start_pos):
        height, width = len(map_data), len(map_data[0])
        visited = [[False] * width for _ in range(height)]
        queue = deque([start_pos])
        visited[start_pos[1]][start_pos[0]] = True

        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if not visited[ny][nx]:
                        if map_data[ny][nx] == self.floor:
                            visited[ny][nx] = True
                            queue.append((nx, ny))
                        elif map_data[ny][nx] == self.wall:
                            if random.random() < 0.3:  # 30% 的概率打通墙壁
                                map_data[ny][nx] = self.floor
                                visited[ny][nx] = True
                                queue.append((nx, ny))

        # 将所有��访问的点设置为墙
        for y in range(height):
            for x in range(width):
                if not visited[y][x]:
                    map_data[y][x] = self.wall

    def is_solvable(self, map_data):
        player_pos = None
        boxes = []
        targets = []

        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                if cell == self.player:
                    player_pos = (x, y)
                elif cell == self.box:
                    boxes.append((x, y))
                elif cell == self.target:
                    targets.append((x, y))
                elif cell == self.box_on_target:
                    boxes.append((x, y))
                    targets.append((x, y))

        if not player_pos or len(boxes) != len(targets):
            return False

        reachable = self.get_reachable_positions(map_data, player_pos)
        
        if not all(target in reachable for target in targets):
            return False

        for box in boxes:
            if self.is_deadlock(map_data, box):
                return False

        return True

    def get_reachable_positions(self, map_data, start_pos):
        height, width = len(map_data), len(map_data[0])
        visited = set()
        queue = deque([start_pos])

        while queue:
            x, y = queue.popleft()
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and map_data[ny][nx] != self.wall:
                        queue.append((nx, ny))

        return visited

    def is_deadlock(self, map_data, pos):
        x, y = pos
        # 检查是否是角落死锁
        if (map_data[y][x-1] == self.wall and map_data[y-1][x] == self.wall) or \
           (map_data[y][x+1] == self.wall and map_data[y-1][x] == self.wall) or \
           (map_data[y][x-1] == self.wall and map_data[y+1][x] == self.wall) or \
           (map_data[y][x+1] == self.wall and map_data[y+1][x] == self.wall):
            return True
        return False

    def get_available_levels(self):
        return list(range(1, self.max_level + 1))

class LevelLoader:
    def __init__(self):
        self.map_generator = MapGenerator()

    def load_level(self, difficulty):
        return self.map_generator.generate_level(difficulty)

    def get_available_levels(self):
        return self.map_generator.get_available_levels()
