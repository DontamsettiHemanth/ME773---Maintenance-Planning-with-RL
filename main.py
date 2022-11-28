import gym

import os

#from huggingface_sb3 import load_from_hub, package_to_hub
#from huggingface_hub import notebook_login
from stable_baselines3 import A2C
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.env_checker import check_env

import torch
from torch import nn

from SimulationEnv import SimulationEnv


env = SimulationEnv()
#print('env space', env.observation_space)
# check_env(env)
# model = A2C("MlpPolicy", env).learn(total_timesteps=T_sim)
