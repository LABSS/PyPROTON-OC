# -*- coding: utf-8 -*-
from mesa import Agent, Model
import random
from extra import *

class Person(Agent):
    pid = 0
    #https://stackoverflow.com/questions/12101958/how-to-keep-track-of-class-instances
    persons = [] 
    network_names = [    
        'sibling',
        'offspring',
        'partner',
        'household',
        'friendship',
        'criminal',
        'professional',
        'school']      
    
    def __init__(self):
        # networks
        self.networks_init()
        self.sentence_countdown = 0
        self.num_crimes_committed = 0
        self.num_crimes_committed_this_tick = 0
        self.education_level = 0     # level: last school I finished (for example, 4: I finished university)
        self.max_education_level = 0
        self.wealth_level = 0
        self.job_level = 0
        self.my_job = 0               # could be known from `one_of job_link_neighbors`, but is stored directly for performance _ need to be kept in sync
        self.birth_tick = 0
        self.male = 0
        self.propensity = 0
        self.oc_member = 0
        self.cached_oc_embeddedness = 0
        self.oc_embeddedness_fresh = 0
        self.partner = 0                # the person's significant other
        self.retired = 0
        self.number_of_children = 0
        self.facilitator = 0
        self.hobby = 0
        self.new_recruit = 0
        self.migrant = 0
        self.age = 0
        self.criminal_tendency = 0
        self.my_school = 0
        self.target_of_intervention = 0
        self.arrest_weight = 0
        #super().__init__(self.unique_id, model)
        self.pid = Person.pid
        Person.pid = Person.pid + 1
        Person.persons.append(self)        
        
#    def random_init(self) : 

    def networks_init(self):
        self.neighbors = {i: set() for i in Person.network_names}
            
    def neighbors_range(self, netname, dist):
        return find_neighb(netname, dist, set(), {self}) - {self}
    
    def step(self):
            pass
#            self.claim()

    def randomfriends(self):
        self.neighbors.get('friendship').add(random.choice(Person.persons))
        self.neighbors.get('friendship').add(random.choice(Person.persons))

class Prisoner(Person):
    sentence_countdown = 0

    def __init__(self):
        self.sentence_countdown = 0
        #super().__init__(self.unique_id, model)
        
if __name__ == "__main__":
    # testing link exploration
    links = [[4,5],[2,3],[1],[1,8],[0,6,5,7],[4,0],[4],[4,8],[9,3,8],[8]]
    for i in range(0,10): 
        p = Person()
    for i in range(0,10): 
        for l in links[i]: Person.persons[i].neighbors.get('friendship').add(Person.persons[l])
    #for i in range(0,10): 
        #print([x.pid for x in Person.persons[i].neighbors.get('friendship')])
    ne = Person.persons[5].neighbors_range('friendship', 3 )
    print([x.pid for x in ne]) # should be [ 4, 7, 8, 0, 6]


