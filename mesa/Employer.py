# -*- coding: utf-8 -*-
import extra
from mesa import Agent, Model
import random
import math
import mesaPROTON_OC
from Job import *
import Person

class Employer():
    max_id = 0
    employers = list()

    def __init__(self, m: mesaPROTON_OC):
        self.my_jobs = list()
        self.m = m
        self.unique_id = Employer.max_id
        Employer.max_id = Employer.max_id + 1
        Employer.employers.append(self)

    def __repr__(self):
        return "Employer: " + str(self.unique_id)
  
    def create_job(self, level: int, worker: Person):
        newjob = Job(self.m)
        newjob.level = level
        worker.my_job = newjob
        self.my_jobs.append(newjob)
        
    def employees(self):
        return [x.my_worker for x in self.my_jobs if x.my_worker != None]


#vjob_level:int, my_employer: Employer, my_worker: Person, m: mesaPROTON_OC.MesaPROTON_OC
#schools-own [
  #diploma-level ; finishing this school provides the level here
  #my-students