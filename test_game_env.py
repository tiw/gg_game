import unittest
from game_env import GameEnv, Action

class TestGameEnv(unittest.TestCase):

    def setUp(self):
        self.env = GameEnv()

    def test_reset(self):
        state = self.env.reset()
        self.assertEqual(state.tolist(), [5, 0, 5, 0], "Reset state should be [5, 0, 5, 0]")

    def test_opponent_action(self):
        action = self.env.opponent_action()
        self.assertIn(action, self.env.action_space, "Opponent action should be in action space")

    def test_step_attack_defend(self):
        self.env.reset()
        # 假设玩家攻击，对手防御，检查对手的能量是否增加
        next_state, reward, done = self.env.step(Action.ATTACK, Action.DEFEND)
        self.assertEqual(next_state.tolist()[3], 1, "Opponent energy should increase when defending against an attack")

    def test_step_gather_energy(self):
        self.env.reset()
        # 假设玩家和对手都gather，检查双方的能量
        next_state, reward, done = self.env.step(Action.GATHER, Action.GATHER)
        self.assertEqual(next_state.tolist()[1], 1, "Player energy should increase when gathering")
        self.assertEqual(next_state.tolist()[3], 1, "Opponent energy should increase when gathering")

    def test_game_end_by_health(self):
        self.env.reset()
        # 通过攻击将对手血量降至0，结束游戏
        for _ in range(5):
            self.env.step(Action.ATTACK, Action.GATHER)
        _, _, done = self.env.step(Action.ATTACK, Action.GATHER)
        print(done)
        self.assertTrue(done, "Game should end when health of one party reaches 0")

    def test_game_end_by_max_step(self):
        self.env.reset()
        # 模拟达到最大步数
        for _ in range(self.env.max_step):
            self.env.step(Action.GATHER, Action.GATHER)
        _, _, done = self.env.step(Action.GATHER, Action.GATHER)
        self.assertTrue(done, "Game should end when max step is reached")

if __name__ == '__main__':
    unittest.main()
