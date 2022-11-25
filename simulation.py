import torch as t

device = "cuda:0" if t.cuda.is_available() else 'cpu'
high_speed= 2
normal_speed = 1
low_speed = 0
t.random.manual_seed(0)
class component:
    def __init__(self,beta,eta,age=0,Reliability=1):
        self.beta = beta # beta for [low,medium,high] operation speed
        self.eta = eta   # beta for [low,medium,high] operation speed
        self.age = age   # age in normal speed
        self.R = Reliability # current reliability
    def failure_time(self,speed):
        u = t.random()
        # age_t = self.eta[speed]*t.pow(-t.log(self.R),1/self.beta[speed]) # virtual age for this speed/phase
        t_f = self.eta[speed]*t.pow(-t.log(u*self.R),1/self.beta[speed])
        return t_f
class system:
    def __init__(self,num_parallel_comps_list,failure_para):
        """
        num_parallel_comps_list - list of number of parralel components at each serial junction
        failure_para - failure parameters(beta[shape para] and eta[scale para]) for each component
        
        """
        self.num_comp = len(failure_para)
        self.num_phases = len(failure_para[0])


def simulate(sys,x,t):