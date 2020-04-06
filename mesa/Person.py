# -*- coding: utf-8 -*-
from mesa import Agent, Model
import uuid
from mesaPATAgent   import PATAgent
import random

class Person(Agent):
    pid
    persons        
    
    def __init__(self, model):
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
        super().__init__(self.unique_id, model)
        Person.pid = Person.pid + 1        
        
    def random_init(self) :          
        personality = Pp.Create_personas()
        personality_mix = personality.Get_personas()
        general_attributes_A = { 'uuid': self.unique_id,
                                'type': 'A',
                                'name': self.name,
                                'token_wallet': {"reputation": 0},
                                'activity': 0,
                                'own_PATs': 0}
        general_attributes_A.update(personality_mix)
        general_attributes_A.update(personality_mix)
        self.attrib = general_attributes_A
        # print("------------random agent---------------")
        # print(general_attributes_A)
        # print("---------------------------")


        
    def custom_init(self, claimer_intention, compliance, voter, creator_intention, creator_design):
        general_atr_A = {'uuid': self.unique_id,
                                'type': 'A',
                                'name': self.name,
                                'token_wallet': {"reputation": 0},
                                'activity': 0,
                                'own_PATs': 0}
        custom_persona= {'claimer': compliance,
                             'claimer_PAT_intention': claimer_intention,
                             'voter': voter,
                             'creator_intention': creator_intention,
                             'creator_design': creator_design}

        self.attrib = (lambda d: d.update(custom_persona) or d)(general_atr_A)
        # print("-----------custom agent----------------")
        # print(self.attrib)
        # print("---------------------------")

    def claim(self):
        # here I claim just one token. Should I instead claim as many as possible?
        pats = PATAgent.pats
        if self.attrib['compliance'] == 'compliant' :
            pat = random.choice(pats)
            act = True
        elif self.attrib['compliance'] == 'opportunistic' :
            pat = random.choice(pats)
            if pat.attrib['design'] == 'careful' :
                act = True
            else :
                act = random.choice([True, False])
        elif self.attrib['compliance'] == 'cheater' :
            pat = random.choice(filter(lambda x: x.attrib['design'] == 'careless', pats) )
            act = False
        if act :
            self.attrib['activity'] = self.attrib['activity'] + 1
            pat.attrib['activity'] =  pat.attrib['activity'] + 1
        self.attrib['token_wallet'] = self.attrib.get('token_wallet', 0) + 1
        
    def create_pat(self):
        #if s['timestep'] > 0 and s['timestep'] % creation_frequency == 0:
        #creator_name = random.randrange(len(agents))
        #print ("creator_name: ", creator_name)
        p = PATAgent()
        p.custom_init(self.attrib['creator_intention'], 
                      self.attrib['creator_design'], 
                      self.attrib['name'])
        
        def step(self):
            self.claim()


class Prisoner(Person):
      sentence-countdown

    def __init__(self, model):
        self.sentence_countdown = 0
        super().__init__(self.unique_id, model)
        
if __name__ == "__main__":
    m = Model()        
    a = HumanAgent(m)
    a.random_init()
    
    b = HumanAgent(m)
    b.custom_init(1,2,3,4,5)