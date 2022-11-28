import gym
from gym import spaces
import numpy as np
import simulation_np as sim
"""
    TODO
    - normalize input states and decode output states in SimulationEnv.step function


    """
np.random.seed(0)
dtype = sim.dtype
N_DISCRETE_ACTIONS = len(sim.ACTIONS)
past_ages = 0  # number of past ages of components to include in state
# system definition
series_parallel_sys = [1]
n_comps = np.sum(series_parallel_sys)
failure_para = np.array([[[1.5, 1500], [2, 1000], [4, 500]]
                        for i in range(n_comps)], dtype=dtype)
initial_ages = np.zeros(n_comps, dtype=dtype)
max_production_rate = failure_para.shape[1]  # also equal to number of phases
T_sim = 1e4


class SimulationEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self):

        N_comp = n_comps
        super(SimulationEnv, self).__init__()

        self.action_space = spaces.MultiDiscrete(
            np.ones((N_comp,))*N_DISCRETE_ACTIONS)  # multidiscrete actions: Each component (do nothing(0),repair(1),replace(2))
        self.sim_step_period = 1
        self.sim_time = 0
        self.total_sim_time = T_sim

        # +2 is for current time and production rate variables
        N_states = (N_comp+2)*(past_ages+1)
        low = np.zeros(N_states, dtype=dtype)
        high = np.ones(N_states, dtype=dtype)*np.inf
        for i in range(past_ages+1):
            idx = i*(N_comp+2) + (N_comp+1)
            high[idx] = max_production_rate
        #print('N_states = ', high.shape, low.shape)
        # self.observation_space = spaces.Box(
        #     low=low, high=high, shape=(N_states,), dtype=dtype)
        self.observation_space = spaces.Box(
            low=low, high=high, dtype=dtype)
        self.sim_system = sim.system(
            series_parallel_sys, failure_para, initial_ages)

    def step(self, action):
        para = self.sim_system.step(
            action, self.sim_step_period, sim.normal_speed)
        self.sim_time += 1
        speed = sim.normal_speed

        observation = np.array(
            para['S_{t+1}'] + [self.sim_time, speed], dtype=dtype)
        # return observation, reward, done, info
        #print('----', observation, observation.dtype)
        return observation, para['R_t'], (self.sim_time >= self.total_sim_time), {}

    def reset(self):
        self.sim_time = 0
        speed = sim.normal_speed
        self.sim_system.reset()
        observation = np.array(
            self.sim_system.get_state() + [self.sim_time, speed], dtype=dtype)
        #print('observation.shape =', observation.shape)
        # reward, done, info can't be included
        #print(observation, observation.dtype)
        return observation  # .reshape((-1,))

    def render(self, mode='human'):
        pass

    def close(self):
        pass
