import pgzrun
import time
import math
from pygame.math import Vector2
import pygame
import sys
from settings import *  # Import the settings

# Custom Actor subclass with disappearing behavior
class TimedActor(Actor):
    def __init__(self, image, pos, disappear_after=2):
        super().__init__(image, pos)
        self.disappear_after = disappear_after
        self.creation_time = time.time()

    def update(self, dt):
        if time.time() - self.creation_time >= self.disappear_after:
            self.disappear()

    def disappear(self):
        self.pos = (-100, -100) 

# The Player class
class Player(Actor):
    def __init__(self, name, position):
        super().__init__(name + '_front')
        # Image names - adjust based on your actual image files
        self.images = {
            'front': name + '_front',
            'laser': name + '_laser',
            'jump': name + '_jump',
            'hurt': name + '_hurt',
            'gather': name + '_gather'
        }
        self.bee_image = "bee_move"
        self.blood = INIT_BLOOD
        self.pos = position 
        self.stand_image = self.images['front'] 

    def draw_hearts(self, start_pos, step=15, heart_type='emote_heart'):
        for i in range(self.blood):
            heart = Actor(heart_type, (start_pos + step * i, 300))
            heart.draw()
        for j in range(self.blood, INIT_BLOOD):
            heart = Actor('emote_heart_broken', (start_pos + step * j, 300))
            heart.draw()

    def take_damage(self, damage=1):
        self.image = self.images['hurt']
        if self.blood > 0:
            self.blood -= damage
        self._surf = pygame.transform.flip(self._surf, True, False)  # Flip if needed

    def fire(self):
        self.image = self.images['jump']
        laser_pos = (self.pos[0] + 50, self.pos[1])
        laser = Laser(self.images['laser'], laser_pos, self.angle)
        return laser

    def defend(self):
        self.image = self.images['front']
        return Shield('shield1', self.pos)

    def gather(self):
        self.image = self.images['gather']

    def ult(self):
        self.image = self.images['jump']
        bee_pos = (self.pos[0] + 50, self.pos[1])
        bee = Bee(self.bee_image, bee_pos, self.angle)
        return bee

    def reset_image(self):
        self.image = self.stand_image


class Laser(Actor):
    def __init__(self, image, pos, angle):
        super().__init__(image, pos)
        self.angle = angle
        self.start_pos = Vector2(pos)
        self.velocity = Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))).normalize() * LASER_SPEED

    def update(self, dt):
        self.pos += self.velocity * dt


class Bee(Actor):
    def __init__(self, image, pos, angle):
        # ... Similar to Laser, but adjust speed using BEE_SPEED
        pass 

class Shield(TimedActor):
    def __init__(self, image, pos):
        super().__init__(image, pos, disappear_after=SHIELD_DURATION)

# ... (Rest of the code in the next response)


# ... (Previous code) 

class GameState():
    lasers = []
    bees = []
    enemy_lasers = []
    enemy_bees = []
    shields = []
    game_over = []
    game_over_images = ['keyboard_g_outline', 'keyboard_a_outline', 'keyboard_m_outline', 'keyboard_e_outline',
                        'keyboard_o_outline', 'keyboard_v_outline','keyboard_e_outline', 'keyboard_r_outline']


game = GameState()

player_a = Player('p1', (100, 400))
player_a.ang = 0 
player_b = Player('p2', (924, 400))
player_b.ang = 180


def update_player_lasers(lasers):
    for laser in lasers:
        laser.update(dt)
        # Check for collisions with enemy shields and player_b
        if laser.colliderect(player_b) or laser.collidelist(game.shields) != -1:
            lasers.remove(laser)
            if laser.colliderect(player_b):  # Only take damage when hitting player directly
                player_b.take_damage()  


def update_enemy_lasers(lasers):
    for laser in lasers:
        laser.angle = 270  # To make them shoot to the left
        laser.update(dt)
        # Check for collisions with player_a and shields:
        if laser.colliderect(player_a) or laser.collidelist(game.shields) != -1:
            lasers.remove(laser)
            if laser.colliderect(player_a):  # Damage when hitting player directly
                player_a.take_damage()  

def update_bees(bees):
    for bee in bees:
        bee.update(dt)  # Update the bee's position based on its velocity
        # Check for collisions with the opposite player
        if bee.owner == 'player_a' and bee.colliderect(player_b):  
            bees.remove(bee)
            player_b.take_damage(damage=2)  
        elif bee.owner == 'player_b' and bee.colliderect(player_a): 
            bees.remove(bee)
            player_a.take_damage(damage=2)  


def check_game_over():
    if player_a.blood <= 0 or player_b.blood <= 0:
        i = 0
        for img_name in game.game_over_images:
            game.game_over.append(Actor(img_name, (WIDTH / 2 - 150 + i, HEIGHT / 2)))
            i += 50

def update(dt):
    update_player_lasers(game.lasers)
    update_enemy_lasers(game.enemy_lasers)
    update_bees(game.bees)
    update_bees(game.enemy_bees)
    check_game_over()

    for shield in game.shields:
        shield.update(dt)

    if keyboard.q:
        sys.exit()


def on_key_down(key):
    # ... (Your existing key handling code)

    if key == keys.K_3:
        laser = player_b.fire()
        game.enemy_lasers.append(laser)

    if key == keys.K_4:
        game.shields.append(player_b.defend())

    if key == keys.K_5:
        player_a.gather()

    if key == keys.K_6:
        player_b.gather()

    if key == keys.K_7:
        bee = player_a.ult()
        bee.owner = 'player_a'  # Mark the owner of the bee
        game.bees.append(bee)

    if key == keys.K_8:
        bee = player_b.ult()
        bee.owner = 'player_b'  # Mark the owner of the bee
        game.enemy_bees.append(bee)


def draw():
    screen.clear()
    screen.blit('bg_desert', (0, 0)) 
    player_a.draw()
    player_b.draw()
    player_a.draw_hearts(80)
    player_b.draw_hearts(904)

    for entity in [game.lasers, game.enemy_lasers, game.bees, game.enemy_bees, game.shields, game.game_over]:
        for item in entity:
            item.draw()

pgzrun.go()
