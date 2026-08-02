import numpy as np
import json
import math
import os

class QLearner:
    def __init__(self, actions=['buy', 'sell', 'hold']):
        self.actions = actions
        self.q_table = {} # State -> {action: value}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1

    def get_state(self, rsi, log_ret, bb_pos):
        rsi_state = "low" if rsi < 30 else ("high" if rsi > 70 else "mid")
        ret_state = "pos" if log_ret > 0 else "neg"
        return f"{rsi_state}_{ret_state}_{bb_pos}"

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
        
        # Q-Learning update
        self.q_table[state][action] = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
