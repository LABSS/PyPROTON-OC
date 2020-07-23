import extra
from mesa import Agent, Model
import mesaPROTON_OC
import numpy as np

class School():
    max_id = 0
    schools = list()
    def __init__(self, m:mesaPROTON_OC, diploma_level, my_student):
        self.m = m
        self.diploma_level = diploma_level
        self.my_student = my_student
        self.unique_id = School.max_id
        School.max_id = School.max_id + 1
        School.schools.append(self)

    def __repr__(self):
        return "School: " + str(self.unique_id) + " Level: " + str(self.diploma_level)