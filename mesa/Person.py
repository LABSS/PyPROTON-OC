# -*- coding: utf-8 -*-
from mesa import Agent, Model
import random
from extra import *
import math
import mesaPROTON_OC

class Person(Agent):
    max_id = 0
    #https://stackoverflow.com/questions/12101958/how-to-keep-track-of-class-instances
    # note that if we run multiple models, persons will be all the ones created in any of them
    persons = [] 
    network_names = [    
        'sibling',
        'offspring',
        'parent'
        'partner',
        'household',
        'friendship',
        'criminal',
        'professional',
        'school']      
    
    def __init__(self, m: mesaPROTON_OC):
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
        self.gender = 0
        self.father = None
        self.mother = None
        self.propensity = 0
        self.oc_member = 0
        self.cached_oc_embeddedness = 0
        self.oc_embeddedness_fresh = 0
        self.partner = None       # the person's significant other
        self.retired = False
        self.number_of_children = 0
        self.facilitator = 0
        self.hobby = 0
        self.new_recruit = 0
        self.migrant = 0
        self.criminal_tendency = 0
        self.my_school = None
        self.target_of_intervention = 0
        self.arrest_weight = 0
        #super().__init__(self.unique_id, model)
        self.unique_id = Person.max_id
        Person.max_id = Person.max_id + 1
        Person.persons.append(self)
        #print(m)
        self.m=m
        #print(" ".join(["I am person", str(self.unique_id), "and my model is", str(self.m)]))
    
    def age(self):
        return math.floor(self.m.ticks - self.birth_tick) / 12

        
    def random_init(self):
        self.randomfriends()
        self.education_level = random.choice(range(0,4))
        self.max_education_level = self.education_level
        self.wealth_level = random.choice(range(0,4))
        self.job_level = random.choice(range(0,4))
        self.my_job = 0               # could be known from `one_of job_link_neighbors`, but is stored directly for performance _ need to be kept in sync
        self.birth_tick = -1 * random.choice(range(0,80*12))
        self.gender = random.choice([0,1])
        self.hobby = 0


    def networks_init(self):
        self.neighbors = {i: set() for i in Person.network_names}
            
    def neigh(self, netname):
        return self.neighbors.get(netname)

    def neighbors_range(self, netname, dist):
        return find_neighb(netname, dist, set(), {self}) - {self}
    
    def step(self):
            pass

    def randomfriends(self):
        for net in Person.network_names:
            for i in range(0,random.randint(0,min(len(Person.persons), 100))):
                self.neighbors.get(net).add(random.choice(Person.persons))
            self.neighbors.get(net).discard(self)
            
    def NumberOfLinks():
        return sum([ 
            sum([
                len(x.neighbors.get(net)) for x in Person.persons 
                ])
            for net in Person.network_names])
    staticmethod(NumberOfLinks)
    
    def makeFriends(self, asker):
        self.neighbors.get("friendship").add(asker)
        asker.neighbors.get("friendship").add(self)

    def makeProfessionalLinks(self, asker):
        self.neighbors.get("professional").add(asker)
        asker.neighbors.get("professional").add(self)
    
    def remove_link(self, forlorn, kind):
        self.neighbors.get(kind).discard(forlorn)
        forlorn.neighbors.get(kind).discard(self)    
    
    def remove_friendship(self, forlorn): self.remove_link(self, forlorn, 'friendship')
    def remove_professional(self, forlorn): self.remove_link(self, forlorn, 'professional')

    def age_between(self, low, high):
        return self.age() >= low and self.age() < high
    
    def family(self): # maybe add self?
        return self.neighbors.get("sibling").add(self.neighbors.get("offspring")).add(self.neighbors.get("partner"))
    
    def potential_friends(self):
        return self.family().add(self.neighbors.get("school")).add(self.neighbors.get("professional")).remove(self.neighbors.get("friendship")) #minus self.. needed?
    
    def dunbar_number(self):
        return(150-abs(self.age()-30))
    
class Prisoner(Person):
    sentence_countdown = 0

    def __init__(self):
        self.sentence_countdown = 0
        #super().__init__(self.unique_id, model)
        
if __name__ == "__main__":
    pass


