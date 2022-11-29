from gym.envs.registration import register
from SimulationEnv import SimulationEnv
# Example for the CartPole environment
register(
    # unique identifier for the env `name-version`
    id="MaintenanceSystem-v1",
    # path to the class for creating the env
    # Note: entry_point also accept a class as input (and not only a string)
    entry_point='/home/hemanthdontamsetti/Documents/DDsem9/me773Lectures/ME773---Maintenance-Planning-with-RL/SimulationEnv:SimulationEnv',
    # Max number of steps per episode, using a `TimeLimitWrapper`
    max_episode_steps=1e4,
)
