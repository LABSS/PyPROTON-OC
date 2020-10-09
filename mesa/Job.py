# -*- coding: utf-8 -*-
import extra
from mesa import Agent, Model
import random
import math
import mesaPROTON_OC
import Employer
import Person

class Job():
    max_id = 0

    def __init__(self, m: mesaPROTON_OC):
        self.m = m
        self.job_level = 0
        self.my_employer = 0
        self.worker = 0
        self.unique_id = Job.max_id
        Job.max_id = Job.max_id + 1

    def __repr__(self):
        return "Job: " + str(self.unique_id) + " Level: " + str(self.job_level)
  
