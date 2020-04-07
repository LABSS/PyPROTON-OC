from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random
import Person
import pandas as pd
import numpy as np
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
        self.number_weddings_mean = 0
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
        self.data_folder = "../inputs/palermo/data/"
        self.load_stats_tables()
        # self.datacollector = DataCollector(
        #     model_reporters={"Gini": compute_gini},
        #     agent_reporters={"Wealth": "wealth"}
        # )
        # Create agents(
        #mesaConfigCreateAgents.configAgents(self)
        #print(MesaFin4.creation_frequency)
        #self.running = True
        #self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        #self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            print(i)
            self.step()
            #if i % MesaFin4.creation_frequency == 0:
            #random.choice(self.schedule.agents).create_pat()
            
            
    def fix_unemployment(self, correction):
        available =  [x for x in Person.persons if x.age > 16 and x.age < 65 and x.my_school == None]
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
           x.facilitator = True if not x.oc_member and          x.age > 18 and           (random.uniform(0,1) < self.percentage_of_facilitators) else False

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
        self.number_weddings_mean =  marr['mean_marriages']
        self.number_weddings_sd =  marr['std_marriages']

        def wedding(self):
            updated_weddings_mean =  (number_weddings_mean * len(Person.persons) / 1000) / 12
            num_wedding_this_month =  np.random.poisson(updated_weddings_mean)
 
            maritable = [x for x in Person.persons if x.age > 25 and x.age < 55 and x.partner == None]

            while num_wedding_this_month > 0 and len(maritable)>1:
                ego =  random.choice(maritable)
                poolf = ego.neighbors_range("friendship", self.max_accomplice_radius) & maritable
                poolp = ego.neighbors_range("professional", self.max_accomplice_radius) & maritable
                pool = poolp | poolf
                if pool:
                    partner = np.random.choice(pool, 
                                    p=wedding_proximity_with(pool), 
                                    size=(1,),
                                    replace=False)
                    
                    
                    
                    

n = 100000
orange_counter = 0
for i in range(n):
    if "orange" in np.random.choice(candies, 
                                    p=weights, 
                                    size=(1),
                                    replace=False)
        orange_counter += 1
        
                    
      ifelse not any pool
      [ ego =  one_of maritable ]
      [ my_partner =  rnd:weighted_one_of pool [ wedding_proximity_with myself ]
        ask my_partner [ maritable =  other maritable ]
        num_wedding_this_month =  num_wedding_this_month _ 1
        number_weddings =  number_weddings + 1
        conclude_wedding pool my_partner ]
    ]
  ]

if __name__ == "__main__":
        num_co_offenders_dist =  pd.read_csv("../inputs/general/data/num_co_offenders_dist.csv")     
        m = MesaPROTON_OC()
