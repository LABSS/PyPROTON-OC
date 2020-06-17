# -*- coding: utf-8 -*-
from extra import *
from mesa import Agent, Model
import random
import math
import mesaPROTON_OC
import Jobs
import Person

class Employer():
    
    def __init__(self, m: mesaPROTON_OC.MesaPROTON_OC):
        self.my_jobs = []
        self.m = m
  
    def create_job(self,  level:int, worker: Person):
        newjob = Job(level, self, worker, m)
        worker.my_job = newjob
        self.my_jobs.add(newjob)
        self.m = m
        
    def employees(self):
        return [x.worker for x in my_jobs]

#vjob_level:int, my_employer: Employer, my_worker: Person, m: mesaPROTON_OC.MesaPROTON_OC
#schools-own [
  #diploma-level ; finishing this school provides the level here
  #my-students