import numpy as np

class QLearner:
    def __init__(self, actions=['buy', 'sell', 'hold']):
        self.actions = actions
        self.q_table = {} # State -> {action: value}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1 # 10% dropout / exploration rate

    def get_state(self, rsi, log_ret, bb_pos, regime):
        """
        regime: 0 (Bear: SMA50 < SMA200), 1 (Bull: SMA50 > SMA200)
        """
        rsi_state = "low" if rsi < 30 else ("high" if rsi > 70 else "mid")
        ret_state = "pos" if log_ret > 0 else "neg"
        return f"{rsi_state}_{ret_state}_{bb_pos}_{regime}"

    def generate_monte_carlo(self, current_price, mu=0.0001, sigma=0.02, steps=100):
        """
        Generates a price path using Geometric Brownian Motion
        """
        paths = []
        for _ in range(10): # Generate 10 variations
            path = [current_price]
            for _ in range(steps):
                path.append(path[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal()))
            paths.append(path)
        return paths

    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.actions)
        return max(self.q_table[state], key=self.q_table[state].get)

    def learn(self, state, action, reward, next_state):
        if state not in self.q_table: self.q_table[state] = {a: 0.0 for a in self.actions}
        if next_state not in self.q_table: self.q_table[next_state] = {a: 0.0 for a in self.actions}
        
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())
        
        self.q_table[state][action] = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
