import pgzrun
import time
import math
from pygame.math import Vector2

# Game settings
WIDTH = 1024
HEIGHT = 512
INIT_BLOOD = 5


class GameState():
    lasers = []

game = GameState()

# Actors
class Player(Actor):
    def __init__(self, image, position, laser_image, fire_image, hurt_image):
        super().__init__(image)
        self.blood = INIT_BLOOD
        self.hearts = []
        self.pos = position
        self.fire_image = fire_image
        self.laser_image = laser_image
        self.hurt_image = hurt_image
        self.stand_image = image

    def draw_hearts(self, start_pos, step=15, heart_type='emote_heart'):
        for i in range(self.blood):
            heart = Actor(heart_type, (start_pos + step * i, 300))
            heart.draw()
        for j in range(self.blood, INIT_BLOOD):
            heart = Actor('emote_heart_broken', (start_pos + step * j, 300))
            heart.draw()

    def take_damage(self, damage=1):
        self.image = self.hurt_image
        if self.blood > 0:
            self.blood -= damage

    def fire(self):
        self.image = self.fire_image
        laser_pos = (self.pos[0] + 50, self.pos[1])
        ang = self.ang
        laser = Actor(self.laser_image, laser_pos)
        laser.angle = -90
        laser.exact_pos = laser.start_pos = Vector2(self.pos)
        laser.velocity = Vector2(math.cos(ang), math.sin(ang)).normalize() * 300.0
        return laser

player_a = Player('p1_front', (100, 400), 'p1_laser', 'p1_jump', 'p1_hurt')
player_a.ang = 0 
player_b = Player('p2_front', (924, 400), 'p2_laser', 'p2_jump', 'p2_hurt')
player_b.ang = 180

# Key handling
def on_key_down(key):
    if key == keys.K_1:
        # player_a.image = 'p1_jump'  # Ensure this image exists
        laser = player_a.fire()
        game.lasers.append(laser)
        # player_b.take_damage()

    if player_b.image != player_b.stand_image:
        player_b.image = player_b.stand_image

    if key == keys.K_2:  # Placeholder for player B's attack
        player_b.image = 'p2_jump'  # Ensure this image exists
        player_a.take_damage()

def on_key_up(key):
    time.sleep(0.5)
    player_a.image = 'p1_front'  # Reset image after key press
    player_b.image = 'p2_front'

def update(dt):
    for laser in game.lasers:
        laser.exact_pos += (laser.velocity * dt)
        c = laser.collidelist([player_b])
        if c > -1:
            player_b.take_damage()
            game.lasers.remove(laser)
            # time.sleep(0.5)
            # player_b.image =  player_b.stand_image
        # if laser.exact_pos.x < 0 or laser.exact_pos.x > WIDTH:
        #     game.lasers.remove(laser)
        laser.pos = laser.exact_pos.x % WIDTH, laser.exact_pos.y % HEIGHT

# Drawing
cloud_pos = 200, 100
def draw():
    screen.clear()
    screen.blit('bg_desert', (0, 0))
    # let cloud move
    global cloud_pos
    cloud_pos = (cloud_pos[0] + 5) % WIDTH, cloud_pos[1]
    screen.blit('cloud1', cloud_pos)
    player_a.draw()
    player_b.draw()
    player_a.draw_hearts(80)
    player_b.draw_hearts(904)

    for laser in game.lasers:
        laser.draw()

pgzrun.go()
