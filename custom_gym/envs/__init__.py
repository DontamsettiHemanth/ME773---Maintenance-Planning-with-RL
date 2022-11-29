from gym.envs.registration import register

register(id='MaintenanceSystem-v1',
         entry_point='envs.maintenance_env:SimulationEnv'
         )
