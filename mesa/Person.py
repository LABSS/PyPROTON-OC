# -*- coding: utf-8 -*-
import extra
from mesa import Agent, Model
import mesaPROTON_OC
import numpy as np

class Person(Agent):
    max_id = 0
    #https://stackoverflow.com/questions/12101958/how-to-keep-track-of-class-instances
    # note that if we run multiple models, persons will be all the ones created in any of them
    persons = [] 
    network_names = [    
        'sibling',
        'offspring',
        'parent',
        'partner',
        'household',
        'friendship',
        'criminal',
        'professional',
        'school']      
    
    def __init__(self, m:mesaPROTON_OC):
        # networks
        self.model = m
        self.networks_init()
        self.sentence_countdown = 0
        self.num_crimes_committed = 0
        self.num_crimes_committed_this_tick = 0
        self.education_level = 0     # level: last school I finished (for example, 4: I finished university)
        self.max_education_level = 0
        self.wealth_level = 0
        self.job_level = 0
        self.my_job = None               # could be known from `one_of job_link_neighbors`, but is stored directly for performance _ need to be kept in sync
        self.birth_tick = 0
        self.gender_is_male = False #True male False female
        self.father = None
        self.mother = None
        self.propensity = 0
        self.oc_member = False
        self.cached_oc_embeddedness = 0
        self.oc_embeddedness_fresh = 0
        self.retired = False
        self.number_of_children = 0
        self.facilitator = None
        self.hobby = 0
        self.new_recruit = -2
        self.migrant = 0
        self.criminal_tendency = 0
        self.my_school = None
        self.target_of_intervention = 0
        self.arrest_weight = 0
        self.criminal_net_weight = dict()
        #super().__init__(self.unique_id, model)
        self.unique_id = Person.max_id
        Person.max_id = Person.max_id + 1
        Person.persons.append(self)
        #print(model)
        #print(" ".join(["I am person", str(self.unique_id), "and my model is", str(self.model)]))

    def __repr__(self):
        return "Agent: " + str(self.unique_id)

    def age(self):
        return extra._age(self.model.ticks, self.birth_tick)
        
    def random_init(self, random_relationships = False, exclude_partner_net = False):
        self.education_level = self.model.rng.choice(range(0, 4))
        self.max_education_level = self.education_level
        self.wealth_level = self.model.rng.choice(range(0, 4))
        self.job_level = self.model.rng.choice(range(0, 4))
        self.my_job = 0               # could be known from `one_of job_link_neighbors`, but is stored directly for performance _ need to be kept in sync
        self.birth_tick = -1 * self.model.rng.choice(range(0, 80 * 12))
        self.gender_is_male = self.model.rng.choice([True, False])
        self.hobby = 0
        self.criminal_tendency = self.model.rng.uniform(0, 1)
        if random_relationships == True:
            self.random_links(exclude_partner_net)


    def networks_init(self):
        self.neighbors = {i: set() for i in Person.network_names}
            
    def neigh(self, netname):
        return self.neighbors.get(netname)

    def neighbors_range(self, netname, dist):
        return extra.find_neighb(netname, dist, set(), {self}) - {self}
    
    def isneighbor(self, other):
        return any([other in self.neighbors[x] for x in Person.network_names])

    def step(self):
            pass

    def random_links(self, exclude_partner_net=False):
        """
        Caution: Use only in test phase. This function generates blood relations and not, randomly
        :param exclude_partner: exclude partner network
        :return: None
        """
        networks = Person.network_names.copy()
        if exclude_partner_net:
            networks.remove("partner")
        for net in networks:
            for i in range(0, self.model.rng.integers(0, min(len(Person.persons), 100))):
                self.neighbors.get(net).add(self.model.rng.choice(Person.persons))
            self.neighbors.get(net).discard(self)

    @staticmethod
    def NumberOfLinks():
        return sum([ 
            sum([
                len(x.neighbors.get(net)) for x in Person.persons 
                ])
            for net in Person.network_names])
    
    def makeFriends(self, asker):
        """
        Create a two-way friend links in-place
        :param asker: agent
        :return: None
        """
        self.neighbors.get("friendship").add(asker)
        asker.neighbors.get("friendship").add(self)

    def makeProfessionalLinks(self, asker):
        """
        Create a two-way professional links in-place
        :param asker: agent
        :return: None
        """
        if type(asker) == list:
            for person in asker:
                self.neighbors.get("professional").add(person)
                person.neighbors.get("professional").add(self)
        else:
            self.neighbors.get("professional").add(asker)
            asker.neighbors.get("professional").add(self)
        
    def addSiblingLinks(self, targets):
        for x in targets:
            if x != self:
                self.neighbors.get("sibling").add(x)
                x.neighbors.get("sibling").add(self)

    def makeHouseholdLinks(self, targets):
        for x in targets:
            if x != self:
                self.neighbors.get("household").add(x)
                x.neighbors.get("household").add(self)

    def makePartnerLinks(self,asker):
        self.neighbors.get("partner").add(asker)
        asker.neighbors.get("partner").add(self)

    def makeParent_OffspringsLinks(self, asker):
        if type(asker) == list:
            for person in asker:
                self.neighbors.get("offspring").add(person)
                person.neighbors.get("parent").add(self)
        else:
            self.neighbors.get("offspring").add(asker)
            asker.neighbors.get("parent").add(self)

    def makeSchoolLinks(self, asker):
        if type(asker) == list:
            for person in asker:
                self.neighbors.get("school").add(person)
                person.neighbors.get("school").add(self)
        else:
            self.neighbors.get("school").add(asker)
            asker.neighbors.get("school").add(self)

    def addCriminalLink(self, asker):
        """
        Create a two-way criminal links in-place and update the connection weight
        :param asker: agent
        :return: None
        """
        self.neighbors.get("criminal").add(asker)
        self.criminal_net_weight[asker] = 1
        asker.neighbors.get("criminal").add(self)
        asker.criminal_net_weight[self] = 1
            
    def remove_link(self, forlorn, kind):
        self.neighbors.get(kind).discard(forlorn)
        forlorn.neighbors.get(kind).discard(self)    
    
    def remove_friendship(self, forlorn): self.remove_link(self, forlorn, 'friendship')
    def remove_professional(self, forlorn): self.remove_link(self, forlorn, 'professional')

    def age_between(self, low, high):
        return self.age() >= low and self.age() < high
    
    def family(self): # maybe add self?
        return self.neighbors.get("sibling").union(self.neighbors.get("offspring")).union(self.neighbors.get("partner"))
    
    def potential_friends(self):
        return self.family().union(self.neighbors.get("school")).union(self.neighbors.get("professional")).difference(self.neighbors.get("friendship")) #minus self.. needed?
    
    def dunbar_number(self):
        return(150-abs(self.age()-30))
    
    def init_person(self): # person command
        """
        This method modifies the attributes of the person instance based on the model's
        stats_tables as part of the initial setup of the model agents.
        """
        row = extra.weighted_one_of(self.model.age_gender_dist, lambda x: x[-1], self.model.rng)  # select a row from our age_gender distribution
        self.birth_tick =  0 - row[0] * self.model.ticks_per_year      # ...and set age... =
        self.gender_is_male =  bool(row[1]) # ...and gender according to values in that row.
        self.retired = self.age() >= self.model.retirement_age                 # persons older than retirement_age are retired
        # education level is chosen, job and wealth follow in a conditioned sequence
        self.max_education_level = extra.pick_from_pair_list(self.model.edu[self.gender_is_male], self.model.rng)
        # apply model-wide education modifier
        if self.model.education_modifier != 1.0:
            if self.model.rng.random() < abs(self.model.education_modifier - 1):
                self.max_education_level = self.max_education_level + (1 if (self.model.education_modifier > 1) else -1)
                self.max_education_level = len(self.model.edu[True]) if self.max_education_level > len(self.model.edu[True]) else 1 if self.max_education_level < 1 else self.max_education_level
        # limit education by age
        # notice how this deforms a little the initial setup
        self.education_level = self.max_education_level
        for level in sorted(list(self.model.education_levels.keys()), reverse=True):
            max_age = self.model.education_levels.get(level)[1]
            if self.age() <= max_age:
                self.education_level = level - 1
        self.propensity = self.model.lognormal(self.model.nat_propensity_m, self.model.nat_propensity_sigma)

    def enroll_to_school(self, level):
        """
        Given a level of education, this method chooses a school where to enroll the agent
        and modifies my_school atribute in-place.
        :param level: int, level of education to enroll
        """
        self.potential_school = [school for agent in self.neighbors["household"] for school in agent.my_school if school.education_level == level]
        if self.potential_school:
            self.my_school = self.model.rng.choice(self.potential_school)
        else:
            self.potential_school = [x for x in self.model.schools if x.diploma_level == level]
            self.my_school = self.model.rng.choice(self.potential_school)
        self.my_school.my_students.add(self)

    def get_link_list(self, net_name):
        """
        Given the name of a network, this method returns a list of agents within the network.
        If the network is empty, it returns an empty list.
        :param net_name: str, the network name
        :return: list, return an empty list if the network is empty
        """
        agent_net = self.neighbors.get(net_name)
        if len(agent_net) > 0:
            return list(agent_net)
        else:
            return []
    def find_job(self):
        """
        This method assigns a job to the Person based on those available and their level. Modify in-place the
        my_worker attribute of Job and the my_job attribute of Person.
        :return: None
        """
        jobs_pool = [j for j in self.model.jobs if j.my_worker == None and j.job_level == self.job_level]
        if not jobs_pool:
            jobs_pool = [j for j in self.model.jobs if j.my_worker == None and j.job_level < self.job_level]
        if jobs_pool:
            the_job = self.model.rng.choice(jobs_pool, 1)[0]
            self.my_job = the_job
            the_job.my_worker = self

    def factors_c(self):
        """
        This procedure modifies the attribute self.criminal_tendency in-place, based on the characteristics of the agent.
        [employment, education, propensity, crim-hist, crim-fam, crim-neigh, oc-member]
        :return: None
        """
        # employment
        self.criminal_tendency *= 1.30 if self.job_level == 1 else 1.0
        # education
        self.criminal_tendency *= 0.94 if self.education_level >= 2 else 1.0
        # propensity
        self.criminal_tendency *= 1.97 if self.propensity > (np.exp(
            self.model.nat_propensity_m - self.model.nat_propensity_sigma ** 2 / 2) + self.model.nat_propensity_threshold * np.sqrt(
            np.exp(self.model.nat_propensity_sigma) ** 2 - 1) * np.exp(
            self.model.nat_propensity_m + self.model.nat_propensity_sigma ** 2 / 2)) else 1.0
        # crim-hist
        self.criminal_tendency *= 1.62 if self.num_crimes_committed >= 0 else 1.0
        # crim-fam
        self.criminal_tendency *= 1.45 if self.family_link_neighbors() and (
                len([agent for agent in self.family_link_neighbors() if agent.num_crimes_committed > 0]) / len(
            self.family_link_neighbors())) > 0.5 else 1.0
        # crim-neigh
        self.criminal_tendency *= 1.81 if self.get_link_list("friendship") or self.get_link_list("professional") and (
                len([agent for agent in self.get_link_list("friendship") if agent.num_crimes_committed > 0]
                    + [agent for agent in self.get_link_list("professional") if agent.num_crimes_committed > 0]) / len(
            [agent for agent in self.get_link_list("friendship")] + [agent for agent in self.get_link_list(
                "professional")])) > 0.5 else 1.0
        # oc-member
        self.criminal_tendency *= 4.50 if self.oc_member and not (
                self.model.intervention_is_on() and self.model.oc_members_scrutinize) else 1.0

    def family_link_neighbors(self):
        """
        This function returns a list of all agents that have sibling,offspring,partner type connection with the agent.
        :return: list, the agents
        """
        return self.get_link_list("sibling") + self.get_link_list("offspring") + self.get_link_list("partner")



class Prisoner(Person):
    sentence_countdown = 0

    def __init__(self):
        self.sentence_countdown = 0
        #super().__init__(self.unique_id, model)
        
if __name__ == "__main__":
    pass


