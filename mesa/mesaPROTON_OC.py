from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random
import Person
import pandas as pd
import numpy as np
from extra import *
from Person import *
import timeit
#import os.chdir

class MesaPROTON_OC(Model):
    """A simple model of an economy of intentional agents and tokens.
    """
    
    def __init__(self):
        # operation
        self.initial_random_seed = 0
        self.network_saving_interval = 0      # every how many we save networks structure
        self.network_saving_list = 0          # the networks that should be saved
        self.model_saving_interval = 0        # every how many we save model structure
        self.breed_colors = 0           # a table from breeds to turtle colors
        self.this_is_a_big_crime = 0 
        self.good_guy_threshold  = 0
        self.big_crime_from_small_fish = 0 # checking anomalous crimes
        # statistics tables
        self.num_co_offenders_dist = 0  # a list of probability for different crime sizes
        self.fertility_table = 0        # a list of fertility rates
        self.mortality_table = 0
        self.edu_by_wealth_lvl = 0
        self.work_status_by_edu_lvl = 0
        self.wealth_quintile_by_work_status = 0
        self.criminal_propensity_by_wealth_quintile = 0
        self.edu = 0
        self.punishment_length_list = 0
        self.male_punishment_length_list = 0
        self.female_punishment_length_list = 0
        self.arrest_rate = 0
        self.jobs_by_company_size = 0
        self.education_levels = 0  # table from education level to data
        self.c_by_age_and_sex = 0
        self.c_range_by_age_and_sex = 0
        self.labour_status_by_age_and_sex = 0
        self.labour_status_range = 0
        

        # outputs
        self.number_deceased = 0
        self.facilitator_fails = 0
        self.facilitator_crimes = 0
        self.crime_size_fails = 0
        self.number_born = 0
        self.number_migrants = 0
        self.number_weddings = 0
        self.number_weddings_mean = 100
        self.number_weddings_sd = 0
        self.removed_fatherships = 0
        self.criminal_tendency_addme_for_weighted_extraction = 0
        self.criminal_tendency_subtractfromme_for_inverse_weighted_extraction = 0
        self.number_law_interventions_this_tick = 0
        self.correction_for_non_facilitators = 0
        self.number_protected_recruited_this_tick = 0
        self.number_offspring_recruited_this_tick = 0
        self.co_offender_group_histo = 0
        self.people_jailed = 0
        self.number_crimes = 0
        self.crime_multiplier = 0
        self.kids_intervention_counter = 0
        

        
        self.schedule = RandomActivation(self)

        # from graphical interface
        self.initial_agents = 100
        self.max_accomplice_radius = 2
        self.number_arrests_per_year = 30 
        self.ticks_per_year = 12
        self.number_crimes_yearly_per10k = 2000
        self.ticks = 0
        
        # loading data from tables and making first calculations
        self.data_folder = "../inputs/palermo/data/"
        self.load_stats_tables()
        # self.datacollector = DataCollector(
        #     model_reporters={"Gini": compute_gini},
        #     agent_reporters={"Wealth": "wealth"}
        # )
        # this gives the base probability of arrest, propotionally to the number of expected crimes in the first year.
        self.arrest_rate = self.number_arrests_per_year / self.ticks_per_year / self.number_crimes_yearly_per10k / 10000 * self.initial_agents
        
        # --agents initialization--
        for i in range(0,self.initial_agents):
            a = Person(self)
            self.schedule.add(a)
            a.random_init()
            
        # calculations that need the agent number


 
        # Create agents(
        #mesaConfigCreateAgents.configAgents(self)
        #print(MesaFin4.creation_frequency)
        #self.running = True
        #self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.wedding()
        # collect data
        #self.datacollector.collect(self)

    def run_model(self, n):
        for self.ticks in range(n):
            print("step: " + str(self.ticks))
            self.step()
        # timeit.timeit(
        #    'print("step: " + str(self.current_step)); self.step()',
        #    setup = 'gc.enable()', number=10)
            #if i % MesaFin4.creation_frequency == 0:
            #random.choice(self.schedule.agents).create_pat()
            
            
    def fix_unemployment(self, correction):
        available =  [x for x in Person.persons if x.age()> 16 and x.age()< 65 and x.my_school == None]
        unemployed = [x for x in available if x.job_level == 1]
        occupied =   [x for x in available if x.job_level >  1]
        notlooking = [x for x in available if x.job_level == 0]
        ratio_on = len(occupied) / (len(occupied) + len(notlooking))
        if correction > 1.0 :
            # increase unemployment
            for x in random.sample(
                    occupied, ((correction - 1) * len(unemployed) * ratio_on)):
                x.job_level = 1,  # no need to resciss job links as they haven't been created yet.
            for x in random.sample(
                    notlooking, ((correction - 1) * len(unemployed) * (1 - ratio_on))) :
                x.job_level = 1,  # no need to resciss job links as they haven't been created yet.
        else :
    # decrease unemployment
            for x in random.sample(
                    unemployed, ((1 - correction) * len(unemployed))):
                    x.job_level = 2 if random.uniform(0,1) < ratio_on else 0


    def setup_facilitators(self) :
       for x in Person.persons :
           x.facilitator = True if not x.oc_member and            x.age()> 18 and                 (random.uniform(0,1) < self.percentage_of_facilitators) else False

    def read_csv(self, filename):
        return pd.read_csv( self.data_folder + filename + ".csv")            
  # but-first?          to-report read-csv [ base-file-name ]
  #report but-first csv:from-file (word data-folder base-file-name ".csv")



    def load_stats_tables(self):
        self.num_co_offenders_dist =  pd.read_csv("../inputs/general/data/num_co_offenders_dist.csv")
        self.fertility_table =  self.read_csv("initial_fertility_rates")
        self.mortality_table =  self.read_csv("initial_mortality_rates")
        self.edu =  self.read_csv("edu")
        self.edu_by_wealth_lvl =  self.read_csv( "../../palermo/data/edu_by_wealth_lvl")
        self.work_status_by_edu_lvl =  self.read_csv("../../palermo/data/work_status_by_edu_lvl")
        self.wealth_quintile_by_work_status = self.read_csv("../../palermo/data/wealth_quintile_by_work_status")
        self.punishment_length_list = self.read_csv("conviction_length")
  #male_punishment_length_list =  map [ i _> (list (item 0 i) (item 2 i)) ] punishment_length_list
  #female_punishment_length_list =  map [ i _> (list (item 0 i) (item 1 i)) ] punishment_length_list
        self.jobs_by_company_size =  self.read_csv("../../palermo/data/jobs_by_company_size")
        self.c_range_by_age_and_sex =  self.read_csv("crime_rate_by_gender_and_age_range")
        self.c_by_age_and_sex =  self.read_csv("crime_rate_by_gender_and_age")
        self.labour_status_by_age_and_sex =  self.read_csv("labour_status")
        self.labour_status_range = self.read_csv("labour_status_range")
        # further sources:
        # schools.csv table goes into education_levels
        marr =  pd.read_csv("../inputs/general/data/marriages_stats.csv")
        self.number_weddings_mean =  marr['mean_marriages'][0]
        self.number_weddings_sd =  marr['std_marriages'][0]



    def wedding(self):
        corrected_weddings_mean = (self.number_weddings_mean * len(Person.persons) / 1000) / 12
        num_wedding_this_month = np.random.poisson(corrected_weddings_mean) #   if num-wedding-this-month < 0 [ set num-wedding-this-month 0 ] ??? 
        maritable = [x for x in Person.persons if x.age() > 25 and x.age() < 55 and x.partner == None]
        print("marit size: " + str(len(maritable)))
        while num_wedding_this_month > 0 and len(maritable)>1:
            ego =  random.choice(maritable) 
            poolf = ego.neighbors_range("friendship", self.max_accomplice_radius) & set(maritable)
            poolp = ego.neighbors_range("professional", self.max_accomplice_radius) & set(maritable)
            pool = [x for x in (poolp | poolf) if 
                    x.gender != ego.gender and
                    (x.age() - ego.age()) < 8 and
                    x not in ego.neigh("sibling") and
                    x not in ego.neigh("offspring") and ego not in x.neigh("offspring") # directed network
                    ]
            if pool:   #https://www.python-course.eu/weighted_choice_and_sample.php
                partner = np.random.choice(pool, 
                                p=wedding_proximity_with(ego, pool), 
                                size=1,
                                replace=False)[0]
                conclude_wedding(ego,partner)
                maritable.remove(partner)
                num_wedding_this_month -= 1
                self.number_weddings += 1                
            maritable.remove(ego) # removed in both cases, if married or if can't find a partner  

    def intervention_on(self):
        return self.ticks % self.ticks_between_intervention == 0 and \
             self.ticks >= intervention_start and \
             self.ticks <  intervention_end
           
    def socialization_intervene(self):
        potential_targets =  [x for x in schedule.agents if x.age() < 18 and x.age >=6 and x.my_school != None ]
        targets = np.random.choice(potential_targets,
                p=[x.criminal_tendency for x in potential_targets],
                size = math.ceil((targets_addressed_percent / 100 * len(potential_targets)) #    criminal_tendency + criminal_tendency_addme_for_weighted_extraction
                                 )
                )
        if social_support == "educational" or social_support == "all": self.soc_add_educational(targets)
        if social_support == "psychological" or social_support == "all": self.soc_add_psychological(targets)
        if social_support == "more friends" or social_support == "all": 
            self.soc_add_more_friends(targets)
            welfare_createjobs({x for x in schedule.agents if x.gender=='female' and x.neighbors.get('offspring').intersection(set(targets))})
            
    def soc_add_educational(self, targets):
        for x in targets: x.max_education_level =  min(max_education_level + 1, max(education_levels.keys()))          

    def soc_add_psychological(self, targets):
        # we use a random sample (arbitrarily to =  50 people size max) to avoid weighting sample from large populations
        for x in targets:
            support_set = at_most(50,[y for y in schedule.agents if y.num_crimes_committed == 0 and y.age() > x.age()])
        if support_set:
            chosen = np.random.choice(support_set, 
                                      p = [(1 - (y.age() - x.age()) / 120) for y in support_set], 
            size=1,
            replace=False)[0]
            chosen.makeFriends(x)
            
    def soc_add_more_friends(self, targets):
        for x in targets:
            support_set = limited.extraction(schedule.agents.remove(x))
            if support_set: 
                x.makeFriends(random.choices(support_set, 
                                        weights=[self.criminal_tendency_subtractfromme_for_inverse_weighted_extraction - y.criminal_tendency for y in support_set],
                              k=1))
                
        def welfare_intervene(self):
            if welfare_support == "job_mother":
                targets = [x for x in schedule.agents if 
                                x.gender == 'female' and 
                                not x.my_job and 
                                (True if not x.partner else not x.partner.oc_member)
                                ]
            if welfare_support == "job_child":
                targets = [x for x in schedule.agents if 
                                x.age() > 16 and x.age()<24 and
                                not x.my_school and
                                not x.my_job and
                                x.father.oc_member
                                ]
            if targets:
                targets = random.sample(targets, math.ceil(targets_addressed_percent / 100 * len(targets)))
                self.welfare_createjobs(targets)
                
        def welfare_createjobs(self, targets):
            for x in targets:
                the_employer = random.choice(self.employers)
                the_level = x.job_level if x.job_level >= 2 else 2
                the_employer.create_job(the_level, x)
                for y in at_most(20,the_employer.employees):
                    x.makeProfessionalLinks(y)
                    


  # here I have to decide how to manage father and mother links. Just as pointers? Then how do I collapse them into the family network? 
  # for now I think I'll just add another network and keep the redundancy, then we'll see.                      
        def family_intervene(self):
            kids_to_protect = [x for x in schedule.agents if x.age_between(12,18)]
            if family_intervention == "remove_if_caught":
                kids_to_protect = [x for x in kids_to_protect if type(x.father) == Prisoner]
            if family_intervention == "remove_if_OC_member":
                kids_to_protect = [x for x in kids_to_protect if x.father.oc_member]
            if family_intervention == "remove_if_caught_and_OC_member":
                kids_to_protect = [x for x in kids_to_protect if type(x.father) == Prisoner and x.father.oc_member]
            if kids_to_protect:
                # notice that the intervention acts on ALL family members respecting the condition, causing double calls for families with double targets.
                # gee but how comes that it increases with the nubmer of targets We have to do better here
                how_many = math.ceil(self.targets_addressed_percent / 100 * len(kids_to_protect))
                for x in random.sample(kids_to_protect, how_many):
                    kids_intervention_counter += 1                
                    # this also removes household links, leaving the household in an incoherent state.
                    x.neighbor.get('parent').remove(x.father) 
                    # maybe not needed?
                    self.removed_fatherships.add( [((18 * ticks_per_year + birth_tick) - ticks), x.father, x])
                    # at this point bad dad is out and we help the remaining with the whole package
                    family = x.family().add(x)
                    self.welfare_createjobs([y for y in family if y.age()>=16 and not y.job and not y.my_school])
                    self.soc_add_educational([y for y in family if y.age()<18 and not y.job])
                    self.soc_add_psychological(family)
                    self.soc_add_more_friends(family)
                    
        def agents_where(self, reporter):
            return [x for x in self.schedule.agents if eval(reporter)]
        


# NEXT: fix bugs in netlogo
#THEN: devise tests!                                     

# end class. From here, static methods

#warning: for now we don't load up the partner in the partner network
def conclude_wedding(ego, partner):
    for x in [ego, partner]:
        for y in x.neighbors["household"]:
            y.neighbors["household"].discard(x) #shoudl be remove(x) once we finish tests
    ego.neighbors["household"] = {partner}
    partner.neighbors["household"] = {ego}
    ego.partner = partner
    partner.partner = ego
staticmethod(conclude_wedding)
      
if __name__ == "__main__":
    num_co_offenders_dist =  pd.read_csv("../inputs/general/data/num_co_offenders_dist.csv")     

    
        


        
