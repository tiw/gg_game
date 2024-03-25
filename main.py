import pgzrun
import time

# Game settings
WIDTH = 1024
HEIGHT = 512
INIT_BLOOD = 5

# Actors
class Player(Actor):
    def __init__(self, image, position):
        super().__init__(image)
        self.blood = INIT_BLOOD
        self.hearts = []
        self.pos = position

    def draw_hearts(self, start_pos, step=15, heart_type='emote_heart'):
        for i in range(self.blood):
            heart = Actor(heart_type, (start_pos + step * i, 300))
            heart.draw()
        for j in range(self.blood, INIT_BLOOD):
            heart = Actor('emote_heart_broken', (start_pos + step * j, 300))
            heart.draw()

    def take_damage(self, damage=1):
        if self.blood > 0:
            self.blood -= damage

player_a = Player('p1_front', (100, 400))
player_b = Player('p2_front', (924, 400))

# Key handling
def on_key_down(key):
    if key == keys.K_1:
        player_a.image = 'p1_jump'  # Ensure this image exists
        player_b.take_damage()

    if key == keys.K_2:  # Placeholder for player B's attack
        player_b.image = 'p2_jump'  # Ensure this image exists
        player_a.take_damage()

def on_key_up(key):
    time.sleep(0.5)
    player_a.image = 'p1_front'  # Reset image after key press
    player_b.image = 'p2_front'

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

pgzrun.go()
