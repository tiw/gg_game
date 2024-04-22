import pgzrun
import time
import math
from pygame.math import Vector2
import pygame
import sys
# 定义全局变量
WIDTH = 800
HEIGHT = 600
cloud_pos = 200, 100
at_main_game = True
player_A_blood = 10
player_B_blood = 10
damage_per_heart = 2

# 初始化游戏资源
def init():
    global WIDTH, HEIGHT, at_main_game, player_A_blood, player_B_blood, damage_per_heart
    WIDTH = 800
    HEIGHT = 600
    At_main_game = True
    player_A_blood = 10
    player_B_blood = 10
    damage_per_heart = 2

# 定义游戏对象
class Player:
    def __init__(self, name, blood):
        self.name = name
        self.blood = blood
        self.hearts_pos = None

    def draw(self):
        screen.blit(self.name, (self.hearts_pos[0], self.hearts_pos[1]))

    def draw_hearts(self, pos):
        self.hearts_pos = pos
        for i in range(self.blood):
            screen.blit('heart', (pos + i * 50, HEIGHT / 2 - 20))

    def take_damage(self, damage=1):
        self.blood -= damage
        if self.blood <= 0:
            global at_main_game
            at_main_game = False

class Cloud:
    def __init__(self, pos):
        self.pos = pos

    def update(self):
        self.pos = (self.pos[0] + 2) % WIDTH, self.pos[1]
        screen.blit('cloud1', self.pos)

class GameOver:
    def __init__(self, images_list):
        self.images_list = images_list
        self.game_over_images = []

    def show(self):
        for l in self.images_list:
            self.game_over_images.append(Actor(l, (WIDTH / 2 - 150 + i, HEIGHT / 2)))
            i += 50
        global at_main_game
        at_main_game = False

# 定义游戏逻辑
def game_logic():
    if keyboard.q:
        sys.exit()

    for s in game.shields:
        s.update()

    if (player_A.blood <= 0) or (player_B.blood <= 0):
        i = 0
        for l in game.game_over_images:
            game.game_over.append(Actor(l, (WIDTH / 2 - 150 + i, HEIGHT / 2)))
            i += 50

    if at_main_game:
        show_main_game()
    else:
        draw_welcome_screen()

# 绘制游戏界面
def draw():
    if at_main_game:
        print('at_main_game')
        show_main_game()
    else:
        draw_welcome_screen()

pgzrun.go()
