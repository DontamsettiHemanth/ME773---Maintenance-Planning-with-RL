import numpy as np
import torch as t
device = "cuda:0" if t.cuda.is_available() else 'cpu'
high_speed = 2
normal_speed = 1
low_speed = 0
COSTS = {'repair': 1, 'replace': 4, 'failure': 8}
t.random.manual_seed(0)
np.random.seed(0)


class component:
    def __init__(self, params, age=0, Reliability=1):
        self.beta = params[:, 0]  # beta for [low,medium,high] operation speed
        self.eta = params[:, 1]   # beta for [low,medium,high] operation speed
        self.age = age   # age in normal speed
        self.R = Reliability  # current reliability
        self.failed = False

    def failure_time(self, speed):
        u = 1-t.rand(device=device)
        # age_t = self.eta[speed]*t.pow(-t.log(self.R),1/self.beta[speed]) # virtual age for this speed/phase
        t_f = self.eta[speed]*t.pow(-t.log(u*self.R), 1/self.beta[speed])
        return t_f

    def update_age(self):
        speed = normal_speed
        self.age = self.eta[speed]*t.pow(-t.log(self.R), 1/self.beta[speed])


class system:
    def __init__(self, num_parallel_comps_list, failure_para, ini_ages):
        """
        num_parallel_comps_list - list of number of parallel components at each serial junction
        failure_para - failure parameters(beta[shape para],eta[scale para]) for each component
        ini_ages - initial ages of all components
        """
        assert failure_para.shape[0] == ini_ages.shape[0]
        self.num_comp = failure_para.shape[0]
        self.num_phases = failure_para.shape[1]
        self.comps = []
        for i in range(self.num_comp):
            self.comps.append(component(failure_para[i], ini_ages[i]))
        self.structure = num_parallel_comps_list

    def step(self, T, speed, cost_pre=0):
        cost = cost_pre  # costs of performing the action
        T_f = t.zeros(self.num_comp, device=device)
        for idx, comp in enumerate(self.comps):
            T_f[idx] = comp.failure_time(speed)
        failed = self.system_check(T_f, T)
        t_f = T_f.min()
        if t_f >= T:
            self.update_all(T, speed)
            return cost
        else:
            cost += COSTS['failure']
            self.step

    def update_all(self, T, speed):
        """ update components reliabilitys and ages if simulation proceeds to next time step T
        out: none
        Args:
            T (int): time/age to be increased by all components 
        """
        pass

    def system_check(self, T_f, T):
        """_summary_

        Args:
            T_f (int[]): failure times of components sampled
            T (int): max_time of simulation step
        output: if system failed or not, time of failure, component failed
        """
        pass

    def system_FAIL_check(self):
        comp = 0
        for idx, i in enumerate(self.structure):
            fail = True
            for j in range(i):
                if self.comps[comp].failed == False:
                    fail = False
                    break
                comp += 1
            if fail == True:
                return True, idx  # system_failure, point of failure in structure
            comp = np.sum(self.structure[:idx+1])
        return False, -1


def simulate(sys, x, t):
    pass
