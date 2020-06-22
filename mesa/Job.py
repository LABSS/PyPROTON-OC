# -*- coding: utf-8 -*-
import extra
from mesa import Agent, Model
import random
import math
import mesaPROTON_OC
import Employer
import Person

class Job():
    
    def __init__(self, job_level:int, employer: Employer, worker: Person, m: mesaPROTON_OC.MesaPROTON_OC):
        self.job_level = job_level
        self.employer = employer
        self.worker = worker
        self.m = m
  
