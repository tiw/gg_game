import numpy as np
import random
from enum import Enum, auto

class Action(Enum):
    ATTACK = auto()
    DEFEND = auto()
    GATHER = auto()
    ULT = auto()

class GameEnv:
    def __init__(self):
        self.action_space = [action for action in Action]
        self.state_size = 4
        self.action_size = len(self.action_space)
        self.max_step = 300
        self.reset()

    def reset(self):
        self.player_health = 5
        self.opponent_health = 5
        self.player_energy = 0
        self.opponent_energy = 0
        self.step_count = 0
        return self.current_state()

    def current_state(self):
        return np.array([self.player_health, self.player_energy, self.opponent_health, self.opponent_energy])

    def opponent_action(self):
        return random.choice(self.action_space)

    def step(self, player_action, opp_action=None):
        self.step_count += 1
        opp_action = opp_action or self.opponent_action()

        reward = 0
        done = False

        # 处理玩家动作
        reward += self.handle_action(player_action, opp_action, is_player=True)

        # 处理对手动作
        reward += self.handle_action(opp_action, player_action, is_player=False)

        # 检查游戏是否结束
        done, final_reward = self.check_game_end()
        reward += final_reward

        return self.current_state(), reward, done

    def handle_action(self, action, counter_action, is_player):
        reward = 0
        if action == Action.ATTACK and counter_action == Action.ULT and ((self.opponent_energy < 2 and is_player) or (self.player_energy < 2 and not is_player)):
            if is_player:
                self.opponent_health -= 1
            else:
                self.player_health -= 1
            reward += 0.7 if is_player else -0.7
        # 更多动作处理逻辑...

        return reward

    def check_game_end(self):
        done = False
        reward = 0
        if self.player_health <= 0 or self.opponent_health <= 0:
            done = True
            if self.player_health <= 0 and self.opponent_health > 0:
                reward = -10
            elif self.opponent_health <= 0 and self.player_health > 0:
                reward = 10
            else:
                reward = 0  # 平局或双方同时倒下
        if self.step_count >= self.max_step:
            done = True
        return done, reward

    def display_status(self):
        print(f"玩家血量: {self.player_health}, 气: {self.player_energy}")
        print(f"对手血量: {self.opponent_health}, 气: {self.opponent_energy}")
