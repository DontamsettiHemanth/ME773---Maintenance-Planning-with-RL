import numpy as np

high_speed = 1
normal_speed = 0
highest_speed = 2
MAX_age = 1e10
COSTS = {'DN': 0, 'MR': 1, 'PR': 4, 'CR': 8, 'SF': 30}
ACTIONS = {'DN': 0, 'MR': 1, 'PR': 2, 'CR': 3}
# Variable full forms-> Do nothing, Minimal Repair, Preventive Replacement, Corrective Replacement, System failure
rand = np.random
dtype = np.float32


class component:
    def __init__(self, params, age=0.001, Reliability=1):
        self.beta = params[:, 0]  # beta for [low,medium,high] operation speed
        self.eta = params[:, 1]   # beta for [low,medium,high] operation speed
        self.age = age   # age in normal speed
        self.R = Reliability  # current reliability for calculation of failure distribution
        self.failed = False

    def reset(self):
        self.age = 1e-5
        self.R = 1
        self.failed = False

    def update_age(self, action):
        """Task: If performed a maintenance action change in age is updated

        Args:
            action (int): action to be taken described by ACTIONS map variable

        """
        if action == ACTIONS['MR']:
            if not self.failed:
                self.age = max(0.4*self.age, self.age-100)
                self.age_to_RUpdate()
            return COSTS['MR']
        elif action == ACTIONS['PR']:
            cost = COSTS['CR'] if self.failed else COSTS['PR']
            self.reset()
            return cost
        elif action == ACTIONS['CR']:
            self.reset()
            return COSTS['CR']
        elif action == ACTIONS['DN']:
            return COSTS['DN']

    def failure_time(self, speed):
        if self.R <= 1e-5:
            return 0.001
        u = np.array(1-rand.rand(), dtype=dtype)
        # age_t = self.eta[speed]*np.power(-np.log(self.R),1/self.beta[speed]) # virtual age for this speed/phase
        t_f = self.eta[speed]*np.power(-np.log(u*self.R), 1/self.beta[speed])
        return t_f

    def R_to_ageUpdate(self):
        speed = normal_speed
        self.age = self.eta[speed] * \
            np.power(-np.log(self.R), 1/self.beta[speed])
        return

    def age_to_RUpdate(self):
        speed = normal_speed
        self.R = np.exp(-np.power(self.age/self.eta[speed], self.beta[speed]))
        return

    def increase_age(self, T, speed):
        v_age = T + self.eta[speed] * \
            np.power(-np.log(self.R), 1/self.beta[speed])
        self.R = np.exp(-np.power(v_age/self.eta[speed], self.beta[speed]))
        self.R_to_ageUpdate()
        return

    def update_failed(self):
        self.R = 1.0e-6
        self.failed = True
        self.age = MAX_age


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
        # self.structure = np.array(num_parallel_comps_list, dtype=np.int)
        self.structure = num_parallel_comps_list

    def step(self, action, T, speed, cost_pre=0):
        # costs of performing the action
        cost = cost_pre + self.action_cost(action)
        cost = self.step_further(T, cost, speed)
        return {'R_t': -cost, 'S_{t+1}': self.get_state()}

    def get_state(self):
        X = []
        for idx, comp in enumerate(self.comps):
            X.append(comp.age)
        return X

    def step_further(self, T, cost, speed):
        sys_failed, idx_failure = self.system_FAIL_check()
        if sys_failed:
            cost += COSTS['SF']
            return cost
        # failure simulation for time step T
        T_f = np.zeros(self.num_comp)
        #print('T_f.shape0', T_f.shape)
        for idx, comp in enumerate(self.comps):
            T_f[idx] = comp.failure_time(speed)
        #print('T_f.shape1', T_f.shape)
        comp_f, t_f = self.min_time(T_f, T)
        self.comps[comp_f].update_failed()
        self.update_all(t_f, speed)
        sys_failed, idx_failure = self.system_FAIL_check()
        if sys_failed:
            cost += COSTS['SF']
        else:
            if T-t_f < 0.001:
                return cost
            cost = self.step_further(T-t_f, cost, speed)
        return cost

    def min_time(self, T_f, T):
        min_p = [-1, np.inf]
        #print('T_f.shape2', T_f.shape)
        for idx, i in enumerate(T_f):
            if i != 0 and min_p[1] > i:
                min_p = [idx, i]
        return min_p

    def action_cost(self, action):
        """Calculates cost of the maintenance action for the system

        Args:
            action (int[]): indexed according to component number
        returns: cost of performing the action
        """
        cost = 0
        for idx, act in enumerate(action):
            cost += self.comps[idx].update_age(act)
        return cost

    def update_all(self, T, Overall_speed):
        """ update components  ages and failure CDF(reliabilitys) if simulation proceeds to next time step T
        out: none
        Args:
            T (int): time/age to be increased by all components 
        """
        def speed_decide(failed_frac, Overall_speed):

            if failed_frac < 0.33:
                speed = Overall_speed
            elif failed_frac < 0.66:
                speed = min(highest_speed, max(high_speed, Overall_speed+1))
            else:
                speed = highest_speed
            return speed
        comp = 0
        for idx, i in enumerate(self.structure):
            failed = 0
            for j in range(i):
                if self.comps[comp].failed == True:
                    failed += 1
                comp += 1
            speed = speed_decide(failed/i, Overall_speed)
            comp -= i
            for j in range(i):
                if self.comps[comp].failed == False:
                    self.comps[comp].increase_age(T, speed)
                comp += 1

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

    def reset(self):
        for i in range(self.num_comp):
            self.comps[i].reset()
