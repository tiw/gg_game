import pgzrun
import time
import math
from pygame.math import Vector2
import pygame
import sys


# Game settings
WIDTH = 1024
HEIGHT = 512
INIT_BLOOD = 5


class EntityState:
    """通用实体状态类"""
    def __init__(self, position):
        self.position = position
        self.blood = INIT_BLOOD
        self.is_active = True


class GameObject(EntityState):
    """通用游戏对象类"""
    def __init__(self, image, position):
        super().__init__(position)
        self.image = image
        self._surf = None

    @property
    def surf(self):
        """获取或创建对象的图像表面"""
        if not self._surf:
            self._surf = Actor(self.image).surf
        return self._surf

    def draw(self):
        """绘制对象"""
        screen.blit(self.surf, self.position)


class Player(GameObject):
    """玩家类"""
    def __init__(self, name, position, angle):
        super().__init__(f"{name}_front", position)
        self.name = name
        self.angle = angle
        self.weapon = Laser(f"{name}_laser")
        self.ult = Bee(f"{name}_bee_move")
        self.heart_type = f"emote_{name}_heart"
        self.broken_heart_type = f"emote_{name}_heart_broken"

    def draw_health_bar(self, x_offset):
        """绘制生命值条"""
        health_step = 15
        for i in range(self.blood):
            heart = GameObject(self.heart_type, (x_offset + health_step * i, 300))
            heart.draw()
        for j in range(self.blood, INIT_BLOOD):
            heart = GameObject(self.broken_heart_type, (x_offset + health_step * j, 300))
            heart.draw()

    def take_damage(self, damage=1):
        self.blood -= damage
        if self.blood <= 0:
            self.is_active = False

    def fire_weapon(self):
        """发射武器"""
        weapon_pos = (self.position[0] + 50, self.position[1])
        weapon_angle = self.angle
        weapon_instance = self.weapon.spawn(weapon_pos, weapon_angle)
        return weapon_instance

    def use_ult(self):
        """使用终极技能"""
        ult_pos = (self.position[0] + 50, self.position[1])
        ult_angle = self.angle
        ult_instance = self.ult.spawn(ult_pos, ult_angle)
        return ult_instance

class Laser(GameObject):
    """激光类"""
    def __init__(self, image, speed=400.0):
        super().__init__(image)
        self.speed = speed

    def spawn(self, position, angle):
        """创建一个新的激光实例"""
        laser = GameObject(self.image, position)
        laser.velocity = Vector2(math.cos(angle), math.sin(angle)).normalize() * self.speed
        return laser


class Bee(GameObject):
    """蜜蜂类"""
    def __init__(self, image):
        super().__init__(image)

    def spawn(self, position, angle):
        """创建一个新的蜜蜂实例"""
        bee = GameObject(self.image, position)
        bee.angle = angle
        return bee

# 初始化玩家
player_a = Player("p1", (100, 400), 0)
player_b = Player("p2", (924, 400), 180)

# 键盘事件处理
def on_key_down(key):
    if key == keys.K_1:
        laser = player_a.fire_weapon()
        game_objects["lasers"].append(laser)

    if key == keys.K_2:
        game_objects["shields"].append(player_a.defend())

    if key == keys.K_3:
        laser = player_b.fire_weapon()
        game_objects["enemy_lasers"].append(laser)

    if key == keys.K_4:
        game_objects["shields"].append(player_b.defend())

    if key == keys.K_5:
        player_a.gather()

    if key == keys.K_6:
        player_b.gather()

    if key == keys.K_7:
        bee = player_a.use_ult()
        game_objects["bees"].append(bee)

    if key == keys.K_8:
        bee = player_b.use_ult()
        game_objects["enemy_bees"].append(bee)

    if key == keys.Q:
        sys.exit()


def update_game_objects(dt):
    """更新所有游戏对象"""
    for obj_list_name, obj_list in game_objects.items():
        for obj in obj_list.copy():  # 使用 copy() 避免在迭代过程中修改列表
            obj.update(dt)
            if not obj.is_active:
                obj_list.remove(obj)


def update_collision():
    """处理碰撞检测"""
    for laser in game_objects["lasers"]:
        if laser.collides_with(player_b):
            player_b.take_damage()
            game_objects["lasers"].remove(laser)

    for laser in game_objects["enemy_lasers"]:
        if laser.collides_with(player_a):
            player_a.take_damage()
            game_objects["enemy_lasers"].remove(laser)

    for bee in game_objects["bees"]:
        if bee.collides_with(player_b):
            player_b.take_damage(damage=2)
            game_objects["bees"].remove(bee)

    for bee in game_objects["enemy_bees"]:
        if bee.collides_with(player_a):
            player_a.take_damage(damage=2)
            game_objects["enemy_bees"].remove(bee)

    if not player_a.is_active or not player_b.is_active:
        display_game_over()


def display_game_over():
    """显示游戏结束画面"""
    global game_over_shown
    if not game_over_shown:
        for i, image_name in enumerate(game_over_images):
            game_over_objects[i].position = (WIDTH / 2 - 150 + i * 50, HEIGHT / 2)
            game_over_objects[i].is_active = True
        game_over_shown = True


def update(dt):
    update_game_objects(dt)
    update_collision()


def draw():
    screen.clear()
    screen.blit('bg_desert', (0, 0))

    player_a.draw()
    player_a.draw_health_bar(80)
    player_b.draw()
    player_b.draw_health_bar(904)

    for obj_list_name, obj_list in game_objects.items():
        for obj in obj_list:
            obj.draw()

    if game_over_shown:
        for obj in game_over_objects:
            obj.draw()


# Game objects and their initial state
game_objects = {
    "lasers": [],
    "enemy_lasers": [],
    "shields": [],
    "bees": [],
    "enemy_bees": [],
}

game_over_images = [
    "keyboard_g_outline",
    "keyboard_a_outline",
    "keyboard_m_outline",
    "keyboard_e_outline",
    "keyboard_o_outline",
    "keyboard_v_outline",
    "keyboard_e_outline",
    "keyboard_r_outline",
]

game_over_objects = [GameObject(image_name, (-100, -100)) for image_name in game_over_images]
game_over_shown = False

pgzrun.go()