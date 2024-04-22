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
at_main_game = False

font = pygame.font.Font('fonts/zh.ttf' , 60)

class GameState():
    lasers = []
    bees = []
    enemy_lasers = []
    enemy_bees = []
    qi = []
    
    shields = []
    game_over = []
    game_over_images = ['keyboard_g_outline', 'keyboard_a_outline', 'keyboard_m_outline', 'keyboard_e_outline', 
        'keyboard_o_outline', 'keyboard_v_outline','keyboard_e_outline', 'keyboard_r_outline']


game = GameState()
# 自定义的 Actor 子类，添加自动消失的功能
class TimedActor(Actor):
    def __init__(self, image, pos, disappear_after=2):
        super().__init__(image, pos)
        self.disappear_after = disappear_after
        self.creation_time = time.time()

    def update(self):
        # 检查是否超过了消失时间
        if time.time() - self.creation_time >= self.disappear_after:
            self.disappear()

    def disappear(self):
        # 让 Actor 消失的逻辑，这里我们简单地把它移出屏幕
        self.pos = (-100, -100)  # 移到屏幕外部


# Actors
class Player(Actor):
    def __init__(self, name, position):
        super().__init__(name+'_front')
        self.image, self.laser_image, self.fire_image, self.hurt_image , self.gather_image = [name + '_' + i for i in ['front', 'laser', 'jump', 'hurt','gather']]
        self.bee_image = "bee_move"
        self.blood = INIT_BLOOD
        self.hearts = []
        self.pi = 0
        self.pos = position
        self.stand_image = self.image


    # 画出玩家血量
    def draw_hearts(self, start_pos, step=15, heart_type='emote_heart'):
        for i in range(self.blood):
            heart = Actor(heart_type, (start_pos + step * i, 300))
            heart.draw()
        for j in range(self.blood, INIT_BLOOD):
            heart = Actor('emote_heart_broken', (start_pos + step * j, 300))
            heart.draw()

    # 受伤
    def take_damage(self, damage=1):
        self.image = self.hurt_image
        if self.blood > 0:
            self.blood -= damage
        self.image = self.hurt_image
        self._surf = pygame.transform.flip(self._surf, True, False)

    # 开火
    def fire(self):
        self.image = self.fire_image
        laser_pos = (self.pos[0] + 50, self.pos[1])
        ang = self.ang
        laser = Actor(self.laser_image, laser_pos)
        laser.angle = -90
        laser.exact_pos = laser.start_pos = Vector2(self.pos)
        laser.velocity = Vector2(math.cos(ang), math.sin(ang)).normalize() * 400.0
        return laser
    
    # 防御
    def defending(self):
        shield = TimedActor('shield1', self.pos)
        return shield

    # 集气
    def gather(self):
        self.image = self.gather_image 
        print(self.image)
        self.pi += 1

    # 大招
    def ult(self):
        if(self.pi >= 2):
            self.image = self.fire_image
            bee_pos = (self.pos[0] + 50, self.pos[1])
            ang = self.ang
            bee = Actor(self.bee_image, bee_pos)
            bee.angle = 90
            bee.exact_pos = bee.start_pos = Vector2(self.pos)
            bee.velocity = Vector2(math.cos(ang), math.sin(ang)).normalize() * 400.0
            self.pi  -= 2
            return bee 

    # 让小人恢复站立的姿势
    def reset_image(self):
        if self.image != self.stand_image:
            self.image = self.stand_image

player_a = Player('p1', (100, 400))
player_a.ang = 0 
player_b = Player('p2', (924, 400))
player_b.ang = 180

# Key handling
def on_key_down(key):
    global at_main_game
    if at_main_game:
        if key == keys.K_1:
            # player_a.image = 'p1_jump'  # Ensure this image exists
            laser = player_a.fire()
            game.lasers.append(laser)

        if key == keys.K_2:
            game.shields.append(player_a.defending())

        if key == keys.K_0:
            # player_b.image = 'p2_jump'  # Ensure this image exists
            laser = player_b.fire()
            game.enemy_lasers.append(laser)
        if key == keys.K_9:
            game.shields.append(player_b.defending())

        if key == keys.K_3:
            player_a.gather()
    
        if key == keys.K_8:
            player_b.gather()
        if key == keys.K_4:
            bee = player_a.ult()
            if bee:
                game.bees.append(bee)
        if key == keys.K_7:
            bee = player_b.ult()
            if bee:
                game.enemy_bees.append(bee)
    else:
        print('key:', key)
        at_main_game = True
          
        # player_a.reset_image()
        # player_b.reset_image()

def update(dt):
    for laser in game.lasers:
        laser.exact_pos.x = laser.exact_pos.x + 10
        s = laser.collidelist(game.shields)
        z = laser.collidelist(game.enemy_lasers)
        if s > -1 or z > -1:
            game.lasers.remove(laser)  
        c = laser.collidelist([player_b])

        if c > -1:
            player_b.take_damage()
            game.lasers.remove(laser)
        laser.pos = laser.exact_pos.x % WIDTH, laser.exact_pos.y % HEIGHT

    for laser in game.enemy_lasers:
        laser.angle = 90
        laser.exact_pos.x = laser.exact_pos.x - 10 
        s = laser.collidelist(game.shields)

        z = laser.collidelist(game.lasers)

        if s > -1 or z > -1:
            game.enemy_lasers.remove(laser)  
        c = laser.collidelist([player_a])
        if c > -1:
            player_a.take_damage()
            game.enemy_lasers.remove(laser)
        laser.pos = laser.exact_pos.x % WIDTH, laser.exact_pos.y % HEIGHT

    for bee in game.enemy_bees:
        bee.angle = 90
        bee.exact_pos.x = bee.exact_pos.x - 10
        c = bee.collidelist([player_a])
        s = bee.collidelist(game.bees)
        if s > -1:
            game.enemy_bees.remove(bee)
        c = bee.collidelist([player_a])

        if c > -1:
            player_a.take_damage(damage=2)
            game.enemy_bees.remove(bee)
        bee.pos = bee.exact_pos.x % WIDTH, bee.exact_pos.y % HEIGHT

    for bee in game.bees:
        bee.exact_pos.x = bee.exact_pos.x + 10
              
        c = bee.collidelist([player_b])

        z = bee.collidelist(game.enemy_bees)    
       
        if z > -1:
            game.bees.remove(bee)
        c = bee.collidelist([player_b])
        if c > -1:
            player_b.take_damage(damage=2)
            game.bees.remove(bee)
        bee.pos = bee.exact_pos.x % WIDTH, bee.exact_pos.y % HEIGHT

    if (player_a.blood <= 0) or (player_b.blood <= 0):
        i = 0
        for l in game.game_over_images:
            game.game_over.append(Actor(l, (WIDTH / 2 - 150 + i, HEIGHT / 2)))
            i += 50
        global at_main_game
        at_main_game = False
        

    for s in game.shields:
        s.update()

    if keyboard.q:
        sys.exit()
   
# Drawing
cloud_pos = 200, 100


# 游戏主界面
def show_main_game():
    screen.clear()
    screen.blit('bg_desert', (0, 0))
    # let cloud move
    global cloud_pos
    cloud_pos = (cloud_pos[0] + 2) % WIDTH, cloud_pos[1]
    screen.blit('cloud1', cloud_pos)
    player_a.draw()
    player_b.draw()
    player_a.draw_hearts(80)
    player_b.draw_hearts(904)
    for laser_list in [game.lasers, game.enemy_lasers, game.bees, game.enemy_bees]:
        for item in laser_list:
            item.draw()

    # for laser in game.lasers:
    #     laser.draw()
    # for laser in game.enemy_lasers:
    #     laser.draw()
    # for bee in game.enemy_bees:
    #     bee.draw() 
    # for bee in game.bees:
    #     bee.draw()
    for l in game.game_over:
        l.draw()
    for s in game.shields:
        s.draw()


# 欢迎界面
def show_welcome_screen():
    screen.clear()
    bg_image = 'purple'

    # 获取背景图像的大小
    bg_width, bg_height = images.load(bg_image).get_size()

    # 计算需要绘制的行数和列数
    rows = HEIGHT // bg_height + 1
    cols = WIDTH // bg_width + 1

    # 在每个位置绘制背景图像
    for y in range(rows):
        for x in range(cols):
            screen.blit(bg_image, (x * bg_width, y * bg_height))
    # screen.blit('purple', (0, 0))
    welcome_surface = font.render("欢迎来到游戏", True, (0, 0, 0))
    begin_surface = font.render("按任意键开始游戏", True, (0, 0, 0))
    screen.blit(welcome_surface, (WIDTH / 2, HEIGHT / 2))
    screen.blit(begin_surface, (WIDTH / 2, HEIGHT / 2 + 50))


def draw():
    show_welcome_screen()
    if at_main_game:
        print('at_main_game')
        show_main_game()


pgzrun.go()