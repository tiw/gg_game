import pgzrun
import time
import math
from pygame.math import Vector2
import pygame
import sys

# Constants
WIDTH = 1024
HEIGHT = 512
INIT_BLOOD = 5
FONT_PATH = 'fonts/zh.ttf'
FONT_SIZE = 60
at_main_game = False

# Initialize Pygame elements
pygame.init()
font = pygame.font.Font(FONT_PATH, FONT_SIZE)

# Game state class
class GameState:
    def __init__(self):
        self.lasers = []
        self.bees = []
        self.enemy_lasers = []
        self.enemy_bees = []
        self.shields = []
        self.game_over = []
        self.game_over_images = ['keyboard_g_outline', 'keyboard_a_outline', 'keyboard_m_outline', 'keyboard_e_outline', 
                                 'keyboard_o_outline', 'keyboard_v_outline','keyboard_e_outline', 'keyboard_r_outline']

# Create game state instance
cloud_pos = 200, 100

game = GameState()

# Timed Actor class for automatic disappearance
class TimedActor(Actor):
    def __init__(self, image, pos, disappear_after=2):
        super().__init__(image, pos)
        self.disappear_after = disappear_after
        self.creation_time = time.time()

    def update(self):
        if time.time() - self.creation_time >= self.disappear_after:
            self.disappear()

    def disappear(self):
        self.pos = (-100, -100)

# Player class with functionalities
class Player(Actor):
    def __init__(self, name, position):
        image_names = [name + '_' + i for i in ['front', 'laser', 'jump', 'hurt', 'gather']]
        self.images = {name: image for name, image in zip(['front', 'laser', 'fire', 'hurt', 'gather'], image_names)}
        super().__init__(self.images['front'])
        self.bee_image = "bee_move"
        self.blood = INIT_BLOOD
        self.hearts = []
        self.pi = 0
        self.pos = position
        self.stand_image = self.image
        self.ang = 0 if name == 'p1' else 180  # Set angle based on player

    # Draw hearts for player's health
    def draw_hearts(self, start_pos, step=15, heart_type='emote_heart'):
        for i in range(self.blood):
            heart = Actor(heart_type, (start_pos + step * i, 300))
            heart.draw()
        for j in range(self.blood, INIT_BLOOD):
            heart = Actor('emote_heart_broken', (start_pos + step * j, 300))
            heart.draw()

    # Take damage and update image
    def take_damage(self, damage=1):
        self.image = self.images['hurt']
        self.blood -= damage
        self._surf = pygame.transform.flip(self._surf, True, False)

    # Fire laser
    def fire(self):
        self.image = self.images['fire']
        laser_pos = (self.pos[0] + 50, self.pos[1])
        laser = Actor(self.images['laser'], laser_pos)
        laser.angle = -90
        laser.exact_pos = laser.start_pos = Vector2(self.pos)
        laser.velocity = Vector2(math.cos(self.ang), math.sin(self.ang)).normalize() * 400.0
        return laser

    # Create a shield
    def defending(self):
        return TimedActor('shield1', self.pos)

    # Gather energy
    def gather(self):
        self.image = self.images['gather']
        self.pi += 1

    # Use ultimate ability
    def ult(self):
        if self.pi >= 2:
            self.image = self.images['fire']
            bee_pos = (self.pos[0] + 50, self.pos[1])
            bee = Actor(self.bee_image, bee_pos)
            bee.angle = 90
            bee.exact_pos = bee.start_pos = Vector2(self.pos)
            bee.velocity = Vector2(math.cos(self.ang), math.sin(self.ang)).normalize() * 400.0
            self.pi -= 2
            return bee 

    # Reset image to standing position
    def reset_image(self):
        if self.image != self.stand_image:
            self.image = self.stand_image

# Create player instances
player_a = Player('p1', (100, 400))
player_b = Player('p2', (924, 400))

# Key handling function
def on_key_down(key):
    global at_main_game, game
    if at_main_game:
        # Player A actions
        if key == keys.K_1:
            game.lasers.append(player_a.fire())
        elif key == keys.K_2:
            game.shields.append(player_a.defending())
        elif key == keys.K_3:
            player_a.gather()
        elif key == keys.K_4:
            bee = player_a.ult()
            if bee:
                game.bees.append(bee)

        # Player B actions
        elif key == keys.K_0:
            game.enemy_lasers.append(player_b.fire())
        elif key == keys.K_9:
            game.shields.append(player_b.defending())
        elif key == keys.K_8:
            player_b.gather()
        elif key == keys.K_7:
            bee = player_b.ult()
            if bee:
                game.enemy_bees.append(bee)
    else:
        at_main_game = True

# Update game objects
def update(dt):
    # Update and handle collisions for lasers and bees
    for laser_list in [game.lasers, game.enemy_lasers]:
        for laser in laser_list[:]:  # Iterate over a copy to allow removal
            laser.exact_pos.x += 10 if laser_list is game.lasers else -10
            # if laser.collidelist(game.shields) > -1 or laser.collidelist(game.enemy_lasers + game.lasers) > -1:
            #     laser_list.remove(laser)
            if laser.collidelist(game.shields) > -1 or laser.collidelist(game.enemy_lasers if laser_list is game.lasers else game.lasers) > -1:
                laser_list.remove(laser)
            elif laser.collidelist([player_b if laser_list is game.lasers else player_a]) > -1:
                (player_b if laser_list is game.lasers else player_a).take_damage() 
                laser_list.remove(laser)
            laser.pos = laser.exact_pos.x % WIDTH, laser.exact_pos.y % HEIGHT

    for bee_list in [game.bees, game.enemy_bees]:
        for bee in bee_list[:]:
            bee.exact_pos.x += 10 if bee_list is game.bees else -10 
            # if bee.collidelist(game.enemy_bees + game.bees) > -1:
            #     bee_list.remove(bee)
            if bee.collidelist(game.enemy_bees if bee_list is game.bees else game.bees) > -1:
                bee_list.remove(bee) 
            elif bee.collidelist([player_b if bee_list is game.bees else player_a]) > -1:
                (player_b if bee_list is game.bees else player_a).take_damage(damage=2)
                bee_list.remove(bee)
            bee.pos = bee.exact_pos.x % WIDTH, bee.exact_pos.y % HEIGHT

    # Check game over condition
    if player_a.blood <= 0 or player_b.blood <= 0:
        for i, l in enumerate(game.game_over_images):
            game.game_over.append(Actor(l, (WIDTH / 2 - 150 + i * 50, HEIGHT / 2)))
        global at_main_game
        at_main_game = False

    # Update shields
    for s in game.shields[:]:
        s.update()
        if s.pos == (-100, -100):
            game.shields.remove(s)

    # Exit on pressing 'q'
    if keyboard.q:
        sys.exit()

# Drawing functions
def show_main_game(cloud_pos):
    global game
    screen.clear()
    screen.blit('bg_desert', (0, 0))
    screen.blit('cloud1', ((cloud_pos[0] + 2) % WIDTH, cloud_pos[1]))  # Move cloud
    
    # Draw players, hearts, and projectiles
    player_a.draw()
    player_b.draw()
    player_a.draw_hearts(80)
    player_b.draw_hearts(904)

    for laser_list in [game.lasers, game.enemy_lasers, game.bees, game.enemy_bees]:
        for item in laser_list:
            item.draw()

    for l in game.game_over:
        l.draw()
    for s in game.shields:
        s.draw()

# Welcome screen
def show_welcome_screen():
    bg_width, bg_height = images.load('purple').get_size()
    rows = HEIGHT // bg_height + 1
    cols = WIDTH // bg_width + 1

    for y in range(rows):
        for x in range(cols):
            screen.blit('purple', (x * bg_width, y * bg_height))

    welcome_surface = font.render("欢迎来到游戏", True, (0, 0, 0))
    begin_surface = font.render("按任意键开始游戏", True, (0, 0, 0))
    screen.blit(welcome_surface, (WIDTH / 2 - welcome_surface.get_width() / 2, HEIGHT / 2))
    screen.blit(begin_surface, (WIDTH / 2 - begin_surface.get_width() / 2, HEIGHT / 2 + 50))

# Main draw function
def draw():
    global at_main_game
    global cloud_pos
    if at_main_game:
        show_main_game(cloud_pos=cloud_pos)
    else:
        show_welcome_screen()

# Start the game
pgzrun.go()