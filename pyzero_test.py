import time
from pgzrun import *
# 导入舞台拓展能力
WIDTH = 1024
HEIGHT = 512
INIT_BLOOD = 5

player_a = Actor('p1_front')
player_b = Actor('p2_front')
player_a.blood = INIT_BLOOD
player_b.blood = INIT_BLOOD
player_a.pos = 100, 400
player_b.pos = 924, 400

def create_and_position_hearts(start_pos_a, start_pos_b, num_hearts, step=10, heart_type='emote_heart'):
    player_a_hearts = []
    player_b_hearts = []
    for i in range(num_hearts):
        # 使用heart_type参数创建心形标志
        heart_a = Actor(heart_type)
        heart_b = Actor(heart_type)
        # 设置位置
        heart_a.pos = (start_pos_a + step * i, 300)
        heart_b.pos = (start_pos_b + step * i, 300)
        # 将心形标志添加到列表中
        player_a_hearts.append(heart_a)
        player_b_hearts.append(heart_b)
    return player_a_hearts, player_b_hearts


player_a_hearts , player_b_hearts = create_and_position_hearts(80, 904, INIT_BLOOD, 15)

def replace_hearts_with_broken(player_hearts, damage, start_pos, step=-15):
    print("called")
    print(damage)
    for i in range(1, damage+1):
        if i <= len(player_hearts):  # 确保不超过现有的心形标志数量
            # 替换为破碎的心形标志
            print(i)
            print(player_hearts[-i].pos)
            player_hearts[-i] = Actor('emote_heart_broken')
            player_hearts[-i].pos = (start_pos + step * (i-1), 300)
            print(player_hearts[-i].pos)
            # pass

# 80 95 110 125 140

def player_a_attack():
    global player_a
    player_a.image='p1_jump'

def player_b_attack():
    global player_b
    player_b.image='p2_jump'

def on_key_up(key):
    time.sleep(1)
    player_a.image = 'p1_front'

c = 0
def on_key_down(key):
    if keyboard.k_1:
        player_a_attack()
        global c
        c += 1
        replace_hearts_with_broken(player_a_hearts, c, 140)

def draw():
    c = 0
    screen.clear()
    screen.blit('bg_desert', (0, 0))
    screen.blit('cloud1', (200, 100))
    player_a.draw()
    player_b.draw()
    # for heart in player_a_broken_hearts:
    #     heart.draw()
    # for heart in player_b_broken_hearts:
    #     heart.draw()
    for heart in player_a_hearts:
        heart.draw()
    for heart in player_b_hearts:
        heart.draw()