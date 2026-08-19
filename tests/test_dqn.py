"""
Unit tests for Deep Q-Network Agent & State Encoder.
"""

import numpy as np
from ai_models.dqn.agent import DQNAgent
from ai_models.dqn.state_encoder import StateEncoder

def test_state_encoder():
    ego = {"speed": 60.0, "lane": 1}
    traffic = [{"lane": 1, "dist": 50.0, "speed": 40.0}]
    state = StateEncoder.encode(ego, traffic, weather="clear")
    assert isinstance(state, np.ndarray)
    assert len(state) == 16
    assert 0.0 <= state[0] <= 1.0  # speed norm

def test_dqn_agent_act():
    agent = DQNAgent()
    state = np.zeros(16, dtype=np.float32)
    action_idx, action_name, q_val = agent.act(state)
    assert 0 <= action_idx < 5
    assert isinstance(action_name, str)

def test_dqn_reward():
    agent = DQNAgent()
    r_normal = agent.calculate_reward(60.0, 60.0, collision=False, near_miss=False)
    r_collision = agent.calculate_reward(60.0, 60.0, collision=True, near_miss=False)
    assert r_normal > 0.0
    assert r_collision == -100.0
