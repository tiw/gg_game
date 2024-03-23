from pgzrun import *
# 导入舞台拓展能力
WIDTH = 1024
HEIGHT = 512

player_a = Actor('p1_front')
player_b = Actor('p2_front')
player_a.pos = 100, 400
player_b.pos = 924, 400

player_a_heart_1 = Actor('emote_heart')
player_b_heart_1 = Actor('emote_heart')
player_a_heart_1.pos = 80, 300
player_b_heart_1.pos = 904, 300
player_a_heart_2 = Actor('emote_heart')
player_b_heart_2 = Actor('emote_heart')
player_a_heart_2.pos = 90, 300
player_b_heart_2.pos = 914, 300
player_a_heart_3 = Actor('emote_heart')
player_b_heart_3 = Actor('emote_heart')
player_a_heart_3.pos = 100, 300
player_b_heart_3.pos = 924, 300
player_a_heart_4 = Actor('emote_heart')
player_b_heart_4 = Actor('emote_heart')
player_a_heart_4.pos = 110, 300
player_b_heart_4.pos = 934, 300
player_a_heart_5 = Actor('emote_heart')
player_b_heart_5 = Actor('emote_heart')
player_a_heart_5.pos = 120, 300
player_b_heart_5.pos = 944, 300
player_a_heart = [player_a_heart_1, player_a_heart_2, player_a_heart_3, player_a_heart_4, player_a_heart_5]
player_b_heart = [player_b_heart_1, player_b_heart_2, player_b_heart_3, player_b_heart_4, player_b_heart_5]


def draw():
    screen.clear()
    screen.blit('bg_desert', (0, 0))
    screen.blit('cloud1', (200, 100))
    player_a.draw()
    player_b.draw()
    for heart in player_a_heart:
        heart.draw()
    for heart in player_b_heart:
        heart.draw()