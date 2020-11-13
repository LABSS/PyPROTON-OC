import extra
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np
import networkx as nx
from Person import *
from School import School
from Employer import Employer
from Job import Job
import timeit
# import testProton
from itertools import combinations
import os
from numpy.random import default_rng
import time

class MesaPROTON_OC(Model):
    """A simple model of an economy of intentional agents and tokens.
    """

    def __init__(self, seed=None):
        super().__init__(seed=seed)
        self.seed = seed
        self.rng = default_rng(seed)
        self.check_random = [self.rng.random(), self.random.random()]
        # operation
        self.initial_random_seed = 0
        self.network_saving_interval = 0  # every how many we save networks structure
        self.network_saving_list = 0  # the networks that should be saved
        self.model_saving_interval = 0  # every how many we save model structure
        self.breed_colors = 0  # a table from breeds to turtle colors
        self.this_is_a_big_crime = 3
        self.good_guy_threshold = 0.6
        self.big_crime_from_small_fish = 0  # checking anomalous crimes

        # statistics tables
        self.num_co_offenders_dist = 0  # a list of probability for different crime sizes
        self.fertility_table = 0  # a list of fertility rates
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
        self.education_levels = dict()  # table from education level to data
        self.c_by_age_and_sex = 0
        self.labour_status_by_age_and_sex = 0
        self.labour_status_range = 0

        #Intervention
        self.family_intervention = None
        self.removed_fatherships = list()
        self.social_support = None
        self.welfare_support = None

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
        self.schools = list()
        self.jobs = list()
        self.employers = list()

        self.schedule = RandomActivation(self)

        # from graphical interface
        self.initial_agents = 100
        self.intervention = None
        self.max_accomplice_radius = 2
        self.number_arrests_per_year = 30
        self.ticks_per_year = 12
        self.number_crimes_yearly_per10k = 2000
        self.ticks = 0
        self.ticks_between_intervention = 1
        self.intervention_start = 13
        self.intervention_end = 999
        self.num_oc_persons = 30
        self.num_oc_families = 8
        self.education_modifier = 1.0 #education-rate in Netlogo model
        self.retirement_age = 65
        self.unemployment_multiplier = "base"
        self.nat_propensity_m = 1.0
        self.nat_propensity_sigma = 0.25
        self.nat_propensity_threshold = 1.0
        self.oc_members_scrutinize = False
        self.facilitator_repression = False
        self.facilitator_repression_multiplier = 2.0
        self.likelihood_of_facilitators = 0.005

        # Folders definition
        self.mesa_dir = os.getcwd()
        self.cwd = os.path.dirname(self.mesa_dir)
        self.input_directory = os.path.join(self.cwd, "inputs")
        self.palermo_inputs = os.path.join(self.input_directory, "palermo")
        self.eindhoven = os.path.join(self.input_directory, "eindhoven")
        self.general = os.path.join(self.input_directory, "general")
        self.general_data = os.path.join(self.general, "data")

        # loading data from tables and making first calculations
        self.data_folder = os.path.join(self.palermo_inputs, "data")
        self.load_stats_tables()

        # Create agents(
        # mesaConfigCreateAgents.configAgents(self)
        # print(MesaFin4.creation_frequency)
        # self.running = True
        # self.datacollector.collect(self)

    def create_agents(self, random_relationships=False, exclude_partner_net=False):
        for i_agent in range(0, self.initial_agents):
            i_agent = Person(self)
            self.schedule.add(i_agent)
            i_agent.random_init(random_relationships, exclude_partner_net)

    def step(self):
        for agent in self.schedule.agents:
            agent.num_crimes_committed_this_tick = 0
        self.number_law_interventions_this_tick = 0
        if self.intervention_is_on():
            if self.family_intervention:
                self.family_intervene()
            if self.social_support:
                self.socialization_intervene()
            if self.welfare_support:
                self.welfare_intervene()

        self.ticks += 1


        # self.schedule.step()
        # self.wedding()

    def run_model(self, n):
        for self.ticks in range(n):
            print("step: " + str(self.ticks))
            self.step()
        # timeit.timeit(
        #    'print("step: " + str(self.current_step)); self.step()',
        #    setup = 'gc.enable()', number=10)
        # if i % MesaFin4.creation_frequency == 0:
        # random.choice(self.schedule.agents).create_pat()

    def fix_unemployment(self, correction):
        available = [x for x in self.schedule.agents if x.age() > 16 and x.age() < 65 and x.my_school == None]
        unemployed = [x for x in available if x.job_level == 1]
        occupied = [x for x in available if x.job_level > 1]
        notlooking = [x for x in available if x.job_level == 0]
        ratio_on = len(occupied) / (len(occupied) + len(notlooking))
        if correction > 1.0:
            # increase unemployment
            for x in self.rng.choice(
                    occupied, ((correction - 1) * len(unemployed) * ratio_on), replace=False):
                x.job_level = 1,  # no need to resciss job links as they haven't been created yet.
            for x in self.rng.choice(
                    notlooking, (correction - 1) * len(unemployed) * (1 - ratio_on), replace=False):
                x.job_level = 1,  # no need to resciss job links as they haven't been created yet.
        else:
            # decrease unemployment
            for x in self.rng.choice(unemployed, (1 - correction) * len(unemployed), replace=False):
                x.job_level = 2 if self.rng.uniform(0, 1) < ratio_on else 0

    def setup_facilitators(self):
        for agent in self.schedule.agent_buffer(shuffled=True):
            agent.facilitator = True if not agent.oc_member and agent.age() > 18 and (self.rng.uniform(0, 1) < self.likelihood_of_facilitators) else False

    def read_csv_city(self, filename):
        return pd.read_csv(os.path.join(self.data_folder, filename + ".csv"))

    # but-first?          to-report read-csv [ base-file-name ]
    # report but-first csv:from-file (word data-folder base-file-name ".csv")

    def load_stats_tables(self):
        self.num_co_offenders_dist = pd.read_csv(os.path.join(self.general_data, "num_co_offenders_dist.csv"))
        self.fertility_table = self.read_csv_city("initial_fertility_rates")
        self.mortality_table = self.read_csv_city("initial_mortality_rates")
        self.edu = self.df_to_dict(self.read_csv_city("edu"))
        self.age_gender_dist = self.read_csv_city("initial_age_gender_dist").values.tolist()

        self.edu_by_wealth_lvl = self.read_csv_city("edu_by_wealth_lvl")
        self.work_status_by_edu_lvl = self.df_to_dict(self.read_csv_city("work_status_by_edu_lvl"))
        self.wealth_quintile_by_work_status = self.df_to_dict(self.read_csv_city("wealth_quintile_by_work_status"))
        self.punishment_length_list = self.read_csv_city("conviction_length")
        # male_punishment_length_list =  map [ i _> (list (item 0 i) (item 2 i)) ] punishment_length_list
        # female_punishment_length_list =  map [ i _> (list (item 0 i) (item 1 i)) ] punishment_length_list
        self.jobs_by_company_size = self.df_to_dict(self.read_csv_city("jobs_by_company_size"))
        self.c_range_by_age_and_sex = self.df_to_lists(self.read_csv_city("crime_rate_by_gender_and_age_range"))
        self.c_by_age_and_sex = self.read_csv_city("crime_rate_by_gender_and_age")
        self.labour_status_by_age_and_sex = self.df_to_dict(self.read_csv_city("labour_status"), extra_depth=True)
        self.labour_status_range = self.read_csv_city("labour_status_range")
        # further sources:
        # schools.csv table goes into education_levels
        marriage = pd.read_csv(os.path.join(self.general_data, "marriages_stats.csv"))
        self.number_weddings_mean = marriage['mean_marriages'][0]
        self.number_weddings_sd = marriage['std_marriages'][0]

    def wedding(self):
        corrected_weddings_mean = (self.number_weddings_mean * len(self.schedule.agents) / 1000) / 12
        num_wedding_this_month = self.rng.poisson(corrected_weddings_mean)  # if num-wedding-this-month < 0 [ set num-wedding-this-month 0 ] ???
        maritable = [x for x in self.schedule.agents if x.age() > 25 and x.age() < 55 and not x.neighbors.get("partner")]
        print("marit size: " + str(len(maritable)))
        while num_wedding_this_month > 0 and len(maritable) > 1:
            ego = self.rng.choice(maritable)
            poolf = ego.neighbors_range("friendship", self.max_accomplice_radius) & set(maritable)
            poolp = ego.neighbors_range("professional", self.max_accomplice_radius) & set(maritable)
            pool = [x for x in (poolp | poolf) if
                    x.gender_is_male != ego.gender_is_male and
                    (x.age() - ego.age()) < 8 and
                    x not in ego.neigh("sibling") and
                    x not in ego.neigh("offspring") and ego not in x.neigh("offspring")  # directed network
                    ]
            if pool:  # https://www.python-course.eu/weighted_choice_and_sample.php
                partner = self.rng.choice(pool,
                                           p=extra.wedding_proximity_with(ego, pool),
                                           replace=False)
                conclude_wedding(ego, partner)
                maritable.remove(partner)
                num_wedding_this_month -= 1
                self.number_weddings += 1
            maritable.remove(ego)  # removed in both cases, if married or if can't find a partner

    def intervention_is_on(self):
        """
        Returns True if there is an active intervention False otherwise.
        :return: bool
        """
        return self.ticks % self.ticks_between_intervention == 0 and self.intervention_start <= self.ticks < self.intervention_end

    def socialization_intervene(self):
        """
        This procedure is active when the self.social_support attribute is different from None. There are 4
        possible social interventions: educational, psychological, more-friends or all. The intervention has effect on a
        portion of eligible members, determined by "how_many" variable that depends on self.targets_addressed_percent attribute.
        The interventions consist of:
        1. soc_add_educational, the max_education_level attribute of the eligible members is increased by one
        2. soc_add_psychological, a new support member (who has not committed crimes) is added to the friends network
        3. soc_add_more_friends, a new support member (with a low level of tendency to crime) is added to the friends network
        4. welfare_createjobs, new jobs are created and assigned to eligible members (mothers)
        :return: None
        """
        potential_targets = [agent for agent in self.schedule.agents if
                             agent.age() <= 18 and agent.age() >= 6 and agent.my_school != None]
        how_many = int(np.ceil(self.targets_addressed_percent / 100 * len(potential_targets)))
        targets = extra.weighted_n_of(how_many, potential_targets, lambda x: x.criminal_tendency, self.rng)

        if self.social_support == "educational" or self.social_support == "all": self.soc_add_educational(targets)
        if self.social_support == "psychological" or self.social_support == "all": self.soc_add_psychological(targets)
        if self.social_support == "more-friends" or self.social_support == "all": self.soc_add_more_friends(targets)
        # also give a job to the mothers
        if self.social_support == "all": self.welfare_createjobs(agent.mother for agent in self.schedule.agents if agent.mother)

    def soc_add_educational(self, targets):
        """
        This procedure modifies the max_education_level attribute of targets in-place, by adding +1 if possible.
        :param targets: list, of Person objects
        :return: None
        """
        for agent in targets:
            agent.max_education_level = min(agent.max_education_level + 1, max(self.education_levels.keys()))

    def soc_add_psychological(self, targets):
        """
        For each target a new support member (who has not committed crimes) is added to the friends network
        :param targets: list, of Person object
        :return: None
        """
        # we use a random sample (arbitrarily to =  50 people size max) to avoid weighting sample from large populations
        for agent in targets:
            support_set = extra.at_most([support_agent for support_agent in self.schedule.agents if support_agent.num_crimes_committed == 0 and support_agent.age() > agent.age()], 50, self.rng)
            if support_set:
                chosen = extra.weighted_one_of(support_set, lambda x: 1 - abs((x.age() - agent.age()) / 120), self.rng)
                chosen.makeFriends(agent)

    def soc_add_more_friends(self, targets):
        """
        For each target a new friend (with a low level of tendency to crime) is added to the friends network
        :param targets: list, of Person objects
        :return: None
        """
        # todo: calculate max_criminal_tendency could be expensive  Maybe we should only
        #  recalculate it when criminal tendency changes?
        max_criminal_tendency = max([0] + [agent.criminal_tendency for agent in self.schedule.agents])
        for target in targets:
            support_set = extra.at_most([agent for agent in self.schedule.agents if agent != target], 50, self.rng)
            if support_set:
                target.makeFriends(extra.weighted_one_of(support_set, lambda x: max_criminal_tendency - x.criminal_tendency, self.rng))

    def welfare_intervene(self):
        """
        This procedure is active when the self.welfare_support attribute is different from None. There are 2
        possible welfare interventions: job-mother or job-child. These parameters determine the portion of the population
        on which the intervention will have effect. The intervention consists of the application of a single procedures
        on eligible family members:
        1. new jobs are created and assigned to eligible members (mothers or children)
        :return: None
        """
        if self.welfare_support == "job-mother":
            targets = list()
            for mother in [agent.mother for agent in self.schedule.agents if agent.mother]:
                if not mother.my_job and mother.neighbors.get("partner"):
                    if mother.get_link_list("partner")[0].oc_member:
                        targets.append(mother)

        if self.welfare_support == "job-child":
            targets = list()
            for agent in self.schedule.agents:
                if agent.age() > 16 and agent.age() < 24 and not agent.my_school and not agent.my_job and agent.father:
                    if agent.father.oc_member:
                        targets.append(agent)

        if targets:
            how_many = int(np.ceil(self.targets_addressed_percent / 100 * len(targets)))
            targets = self.rng.choice(targets, how_many, replace=False)
            self.welfare_createjobs(targets)

    def welfare_createjobs(self, targets):
        """
        This procedure creates new jobs for each member within targets.
        :param targets: list, of Person objects
        :return: None
        """
        for agent in targets:
            the_employer = self.rng.choice(self.employers)
            the_level = agent.job_level if agent.job_level >= 2 else 2
            the_employer.create_job(the_level, agent)
            for new_professional_link in extra.at_most(the_employer.employees(), 20, self.rng):
                agent.makeProfessionalLinks(new_professional_link)

    def family_intervene(self):
        """
        This procedure is active when the self.family_intervention attribute is different from None. There are 3
        possible family interventions: remove_if_caught, remove_if_OC_member and remove_if_caught_and_OC_member.
        These parameters determine the portion of the population on which the intervention will have effect.
        The intervention consists of the application of 5 procedures on eligible family members:
        1. Fathers who comply with the conditions are removed from their families (Removed fathers are stored within the
        removed_fatherships attribute so it is possible at any time to reintroduce them into the family.)
        2. welfare_createjobs, new jobs are created and assigned to eligible members.
        3. soc_add_educational, the max_education_level attribute of the eligible members is increased by one
        4. soc_add_psychological, a new support member (who has not committed crimes) is added to the friends network
        5. soc_add_more_friends, a new support member (with a low level of tendency to crime) is added to the friends network
        :return: None
        """
        kids_to_protect = [agent for agent in self.schedule.agents if agent.age() < 18 and agent.age() >= 12 and agent.father in agent.neighbors.get("parent")]
        if self.family_intervention == "remove-if-caught":
            kids_to_protect = [agent for agent in kids_to_protect if type(agent.father) == Prisoner]
        if self.family_intervention == "remove-if-OC-member":
            kids_to_protect = [agent for agent in kids_to_protect if agent.father.oc_member]
        if self.family_intervention == "remove-if-caught-and-OC-member":
            kids_to_protect = [agent for agent in kids_to_protect if type(agent.father) == Prisoner and agent.father.oc_member]
        if kids_to_protect:
            how_many = int(np.ceil(self.targets_addressed_percent / 100 * len(kids_to_protect)))
            kids_pool = list(self.rng.choice(kids_to_protect, how_many, replace=False))
            for kid in kids_pool:
                self.kids_intervention_counter += 1
                # notice that the intervention acts on ALL family members respecting the condition, causing double calls for families with double targets.
                # gee but how comes that it increases with the nubmer of targets? We have to do better here
                # this also removes household links, leaving the household in an incoherent state.
                kid.neighbors.get("parent").remove(kid.father)
                kid.father.neighbors.get("offspring").remove(kid)
                self.removed_fatherships.append([((18 * self.ticks_per_year + kid.birth_tick) - self.ticks), kid.father, kid])
                # we do not modify Person.father, this attribute is implemented so that it is possible to remove the father from the network and keep the information.
                # at this point bad dad is out and we help the remaining with the whole package
                # family_links_neighbors also include siblings that could be assigned during setup through the setup_siblings procedure,
                # we do not need these in this procedure
                family = [kid] + kid.family_link_neighbors()
                self.welfare_createjobs([agent for agent in family if agent.age() >= 16 and not agent.my_job and not agent.my_school])
                self.soc_add_educational([agent for agent in family if agent.age() < 18 and not agent.my_job])
                self.soc_add_psychological(family)
                self.soc_add_more_friends(family)

    def agents_where(self, reporter):
        return [x for x in self.schedule.agents if eval(reporter)]

    def return_kids(self):
        for a in removed - fatherships:
            # list tick father son
            if a[2].age() >= 18:
                if self.rng.random() < (6 / a[0]):
                    # check for coherence. Need better offspring design.
                    a[2].networks.get['parents'].add(a[1])
                    a[2].father = a[1]
                    removed.fatherships.remove(a)

    def make_friends(self):
        for a in self.schedule.agent_buffer(shuffled=True):
            p_friends = a.potential_friends()
            num_new_friends = min(len(p_friends), self.rng.poisson(3))
            chosen = self.rng.choice(p_friends,
                                        size=num_new_friends,
                                        p=[extra.social_proximity(x) for x in p_friends],
                                        replace=False)
            for c in chosen:
                c.makeFriends(a)

    def remove_excess_friends(self):
        for a in self.schedule.agents:
            friends = a.neighbors.get('friendship')
            nf = len(friends)
            if nf > a.dunbar_number():
                for c in self.rng.choice(friends, nf - a.dunbar_number(), replace=False):
                    c.remove_friendship(a)

    def remove_excess_professional_links(self):
        for a in self.schedule.agents:
            friends = a.neighbors.get('friendship')
            nf = len(friends)
            if nf > 30:
                for c in self.rng.choice(friends, nf - 30, replace=False):
                    c.remove_professional(a)

    def total_num_links(self):
        return sum([
            sum([len(a.neighbors.get(net))
                 for net in Person.network_names])
            for a in self.schedule.agents]) / 2

    def setup_oc_groups(self):
        """
        This procedure creates "criminal" type links within the families, in case there are not enough members
        takes members from outside.
        :return: None
        """
        # OC members are scaled down if we don't have 10K agents
        scaled_num_oc_families = np.ceil(self.num_oc_families * self.initial_agents / 10000 * self.num_oc_persons / 30)
        scaled_num_oc_persons = np.ceil(self.num_oc_persons * self.initial_agents / 10000)
        # families first.
        # we assume here that we'll never get a negative criminal tendency.
        oc_family_heads = extra.weighted_n_of(scaled_num_oc_families, self.schedule.agents, lambda x: x.criminal_tendency, self.rng)
        for head in oc_family_heads:
            head.oc_member = True
        candidates = [relative for oc_family_head in oc_family_heads for relative in oc_family_head.neighbors.get('household')
                          if relative.age() >= 18]
        if len(candidates) >= scaled_num_oc_persons - scaled_num_oc_families:  # family members will be enough
            members_in_families = extra.weighted_n_of(scaled_num_oc_persons - scaled_num_oc_families, candidates, lambda x: x.criminal_tendency, self.rng)
            # fill up the families as much as possible
            for member in members_in_families:
                member.oc_member = True
        else:  # take more as needed (note that this modifies the count of families)
            for candidate in candidates:
                candidate.oc_member = True
            out_of_family_candidates = [agent for agent in self.schedule.agents if not agent.oc_member]
            out_of_family_candidates = extra.weighted_n_of(scaled_num_oc_persons - len(candidates) - len(oc_family_heads),
                                                           out_of_family_candidates, lambda x: x.criminal_tendency, self.rng)
            for out_of_family_candidate in out_of_family_candidates:
                out_of_family_candidate.oc_member = True
        # and now, the network with its weights..
        oc_members_pool = [oc_member for oc_member in self.schedule.agents if oc_member.oc_member]
        for (i, j) in combinations(oc_members_pool, 2):
            i.addCriminalLink(j)

    def reset_oc_embeddedness(self):
        for x in self.schedule.agents: x.cached_oc_embeddedness = None

    def setup_persons_and_friendship(self):
        # We transform this df into a list for ease of access
        self.watts_strogatz = nx.watts_strogatz_graph(self.initial_agents, 2, 0.1)
        for x in self.watts_strogatz.nodes():
            a = Person(self)
            a.init_person()
            self.schedule.add(a)
            # g.nodes[nlrow['id']].update(nlrow[1:].to_dict())
            self.watts_strogatz.nodes[x].update({'person': a})
        # ['person'].update(2)
        for x in list(self.watts_strogatz.nodes()):  # where do I have seen this instruction before?
            for y in list(self.watts_strogatz.neighbors(x)):
                self.watts_strogatz.nodes[y]['person'].makeFriends(self.watts_strogatz.nodes[x]['person'])
        # nx.draw(watts_strogatz, with_labels=True)
        # plt.show()

    def list_contains_problems(self, ego, candidates):
        """
        This procedure checks if there are any links between partners within the candidate pool.
        Returns True if there are, None if there are not.
        It is used during the setup_siblings procedure to avoid incestuous marriages.
        :param ego: Person
        :param candidates: list of Person objects
        :return: bool, True if there are links between partners, None otherwise.
        """
        all_potential_siblings = [ego] + ego.get_neighbor_list("sibling") + candidates + [sibling for candidate in candidates for sibling in candidate.neighbors.get('sibling')]
        for sibling in all_potential_siblings:
            if sibling.get_neighbor_list("partner") and sibling.get_neighbor_list("partner")[0] in all_potential_siblings:
                return True

    def setup_siblings(self):
        """
        Right now, during setup, links between agents are only those within households, between friends
        and related to the school. At this stage of the standard setup, agents are linked through "siblings" links
        outside the household. To simulate agents who have left the original household, agents who have
        children are taken and "sibling" links are created taking care not to create incestuous relationships.
        :return: None
        """
        agent_left_household = [p for p in self.schedule.agents if p.neighbors.get('offspring')] # simulates people who left the original household.
        for agent in agent_left_household:
            num_siblings = self.rng.poisson(0.5)
            # 0.5 -> the number of links is N^3 agents, so let's keep this low
            # at this stage links with other persons are only relatives inside households and friends.
            candidates = [c for c in agent_left_household if c not in agent.neighbors.get("household") and abs(agent.age() - c.age()) < 5 and c != agent]
            # remove couples from candidates and their neighborhoods (siblings)
            if len(candidates) >= 50:
                candidates = self.rng.choice(candidates, 50, replace=False).tolist()
            while len(candidates) > 0 and self.list_contains_problems(agent, candidates):
                # trouble should exist, or check-all-siblings would fail
                potential_trouble = [x for x in candidates if agent.get_neighbor_list("partner")]
                trouble = self.rng.choice(potential_trouble)
                candidates.remove(trouble)
            targets = [agent] + self.rng.choice(candidates, min(len(candidates),num_siblings)).tolist()
            for sib in targets:
                if sib in agent_left_household:
                    agent_left_household.remove(sib)
            for target in targets:
                target.addSiblingLinks(targets)
                # this is a good place to remind that the number of links in the sibling link neighbors is not the "number of brothers and sisters"
                # because, for example, 4 brothers = 6 links.
            other_targets = targets + [s for c in targets for s in c.neighbors.get('sibling')]
            for target in other_targets:
                target.addSiblingLinks(other_targets)


    def generate_households(self):
        # this mostly follows the third algorithm from Gargiulo et al. 2010
        # (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0008828)
        # The dataframes are transformed into nested dictionaries to ensure greater speed
        self.families = list()
        head_age_dist = self.df_to_dict(self.read_csv_city("head_age_dist_by_household_size"))
        proportion_of_male_singles_by_age = self.df_to_dict(self.read_csv_city("proportion_of_male_singles_by_age"))
        hh_type_dist = self.df_to_dict(self.read_csv_city("household_type_dist_by_age"))
        partner_age_dist = self.df_to_dict(self.read_csv_city("partner_age_dist"))
        self.children_age_dist = self.df_to_dict(self.read_csv_city("children_age_dist"))
        p_single_father = self.read_csv_city("proportion_single_fathers")
        self.population = self.schedule.agents
        self.hh_size = self.household_sizes(self.initial_agents)
        self.complex_hh_sizes = list()  # will contain the sizes that we fail to generate: we'll reuse those for complex households
        max_attempts_by_size = 50
        attempts_list = list()
        # We have two levels of iterating: the first level is the general attempts at generating a household
        # and the second level is the attempts at generating a household of a particular size before giving up.
        for size in self.hh_size:
            success = False
            nb_attempts = 0
            while not success and nb_attempts < max_attempts_by_size:
                hh_members = list()
                nb_attempts += 1
                # pick the age of the head according to the size of the household
                head_age = extra.pick_from_pair_list(head_age_dist[size],self.rng)
                if size == 1:
                    male_wanted = (self.rng.random() < proportion_of_male_singles_by_age[head_age])
                    head = self.pick_from_population_pool_by_age_and_gender(head_age, male_wanted)
                    # Note that we don't "do" anything with the picked head: the fact that it gets
                    # removed from the population table when we pick it is sufficient for us.
                    if head:
                        success = True
                        attempts_list.append(nb_attempts)
                else:
                    # For household sizes greater than 1, pick a household type according to age of the head
                    hh_type = extra.pick_from_pair_list(hh_type_dist[head_age], self.rng)
                    if hh_type == "single_parent":
                        male_head = self.rng.random() < float(p_single_father.columns.to_list()[0])
                    else:
                        male_head = True
                    if male_head:
                        mother_age = extra.pick_from_pair_list(partner_age_dist[head_age], self.rng)
                    else:
                        mother_age = head_age
                    hh_members.append(self.pick_from_population_pool_by_age_and_gender(head_age, male_head))
                    if hh_type == "couple":
                        mother = self.pick_from_population_pool_by_age_and_gender(mother_age, False)
                        hh_members.append(mother)
                    num_children = size - len(hh_members)
                    for child in range(1, int(num_children) + 1):
                        if num_children in self.children_age_dist:
                            if mother_age in self.children_age_dist[num_children]:
                                child_age = extra.pick_from_pair_list(self.children_age_dist[num_children][mother_age], self.rng)
                                child = self.pick_from_population_pool_by_age(child_age)
                                hh_members.append(child)
                    hh_members = [x for x in hh_members if x != None] #exclude Nones
                    if len(hh_members) == size:
                        # only generate the household if we got everyone we needed
                        success = True
                        attempts_list.append(nb_attempts)
                        family_wealth_level = hh_members[0].wealth_level
                        # if it's a couple, partner up the first two members and set the others as offspring
                        if hh_type == "couple":
                            hh_members[0].makePartnerLinks(hh_members[1])
                            couple = hh_members[0:2]
                            offsprings = hh_members[2:]
                            for partner in couple:
                                partner.makeParent_OffspringsLinks(offsprings)
                            for sibling in offsprings:
                                sibling.addSiblingLinks(offsprings)
                        for member in hh_members:
                            member.makeHouseholdLinks(hh_members)
                            member.wealth_level = family_wealth_level
                        self.families.append(hh_members)
                    else:
                        # in case of failure, we need to put the selected members back in the population
                        for member in hh_members:
                            self.population.append(member)
            if not success:
                self.complex_hh_sizes.append(size)
        print("Complex size: " + str(len(self.complex_hh_sizes)) + str("/") + str(len(self.hh_size)))
        for comp_hh_size in self.complex_hh_sizes:
            comp_hh_size = int(min(comp_hh_size, len(self.population)))
            complex_hh_members = self.population[0:comp_hh_size] # grab the first persons in the list
            max_age_index = [x.age() for x in complex_hh_members].index(max([x.age() for x in complex_hh_members]))
            family_wealth_level = complex_hh_members[max_age_index].wealth_level
            for member in complex_hh_members:
                self.population.remove(member) # remove persons from the population
                member.makeHouseholdLinks(complex_hh_members) #and link them up.
                member.wealth_level = family_wealth_level
            if len(complex_hh_members) > 1:
                self.families.append(complex_hh_members)
        print("Singles " + str(len([x for x in self.hh_size if x == 1])))
        print("Families " + str(len(self.families)))
        print("Average of attempts " + str(np.mean(attempts_list)))

    def household_sizes(self, size):
        """
        loads a .csv with a probability distribution of household size and calculates household based on initial agents
        :param size: int, the population size, initial agents
        :return: list, the sizes of household
        """
        hh_size_dist = self.read_csv_city("household_size_dist").values
        sizes = []
        current_sum = 0
        while current_sum < size:
            hh_size = extra.pick_from_pair_list(hh_size_dist, self.rng)
            if current_sum + hh_size <= size:
                sizes.append(hh_size)
                current_sum += hh_size
        sizes.sort(reverse=True)
        return sizes

    def pick_from_population_pool_by_age_and_gender(self, age_wanted, male_wanted):
        """
        Pick an agent with specific age and sex, None otherwise
        :param age_wanted: int, age wanted
        :param male_wanted: bool,
        :return: agent, or None
        """
        if not [x for x in self.population if x.gender_is_male == male_wanted and x.age() == age_wanted]:
            return None
        picked_person = self.rng.choice(
            [x for x in self.population if x.gender_is_male == male_wanted and x.age() == age_wanted])
        self.population.remove(picked_person)
        return picked_person

    def pick_from_population_pool_by_age(self, age_wanted):
        """
        Pick an agent with specific age form population, None otherwise
        :param age_wanted: int, age wanted
        :return: agent or None
        """
        if age_wanted not in [x.age() for x in self.population]:
            return None
        picked_person = self.rng.choice([x for x in self.population if x.age() == age_wanted])
        self.population.remove(picked_person)
        return picked_person

    def df_to_dict(self, df, extra_depth=False):
        """
        Based on the number of pandas DataFrame columns, transforms the dataframe into nested dictionaries as follows:
        df-columns = age, sex, education, p --> dict-keys = {age:{sex:[education, p]}}

        If extra_depth is True the transformation has an extra level of depth as follows:
        df-columns = age, sex, education, p --> dict-keys = {age:{sex:{education: p}}}

        This transformation ensures a faster access to the values using the dictionary keys.
        :param df: pandas df, the df to be transformed
        :param extra_depth: bool, if True gives an extra level of depth
        :return: dict, a new dictionary
        """
        dic = dict()
        extra_depth_modifier = 1 if extra_depth else 0

        for col in np.unique(df.iloc[:, 0]):
            if len(df.columns) + extra_depth_modifier == 2:
                dic[col] = df[df.iloc[:,0] == col].iloc[:,1].values
            if len(df.columns) + extra_depth_modifier == 3:
                dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1:].values
            if len(df.columns) + extra_depth_modifier == 4:
                dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1:]
        if len(df.columns) + extra_depth_modifier == 4:
            for key in dic:
                subdic = dict()
                for subcol in np.unique(dic[key].iloc[:, 0]):
                    if extra_depth:
                        subdic[subcol] = dic[key][dic[key].iloc[:, 0] == subcol].iloc[:, 1:].values[0][0]
                    else:
                        subdic[subcol] = dic[key][dic[key].iloc[:, 0] == subcol].iloc[:, 1:].values
                dic[key] = subdic
        return dic

    def setup_education_levels(self):
        """
        Modify the self.education_levels attribute in-place. Given "n" levels of education,
        for each level compute the correct amount of schools, based on the number of agents.
        """
        self.list_schools = self.read_csv_city("schools").values.tolist()
        for index, level in enumerate(self.list_schools):
            level[3] = np.ceil((level[3]/level[4])*self.initial_agents)
            level.remove(level[4])
            self.education_levels[index+1] = level

    def setup_schools(self):
        """
        Generates n-schools based on the number of initial agents
        """
        for level in self.education_levels.keys():
            for i_school in range(int(self.education_levels[level][3])):
                new_school = School(self, level)
                self.schools.append(new_school)

    def init_students(self):
        """
        Adds to schools the agents that meet the defined parameters of age and level of education and then
        creates connections between agents within the school.
        """
        for level in self.education_levels:
            row = self.education_levels[level]
            start_age = row[0]
            end_age = row[1]
            pool = [x for x in self.schedule.agents if
                    x.age() >= start_age and x.age() <= end_age and x.education_level == level - 1 and x.max_education_level >= level]
            for agent in pool:
                agent.enroll_to_school(level)
        for school in self.schools:
            conn = self.decide_conn_number(school.my_students, 15)
            for student in school.my_students:
                total_pool = school.my_students.difference({student})
                conn_pool = list(extra.at_most(list(total_pool), conn, self.rng))
                student.makeSchoolLinks(conn_pool)

    def decide_conn_number(self, agents, max_lim):
        """
        Given a set of agents decides the number of connections to be created between them based on a maximum number.
        :param agents: list or set, of agents
        :param max_lim: int, an arbitrary maximum number
        :return: max_lim if the agents are more than max_lim otherwise returns the number of agents minus one.
        """
        if len(agents) <= max_lim:
            return len(agents) -1
        else:
            return max_lim

    def setup(self, n_agent):
        """
        Standard setup of the model
        :param n_agent: int, number of initial agents
        """
        self.choose_intervention_setting()
        start = time.time()
        self.initial_agents = n_agent
        self.setup_education_levels()
        self.setup_persons_and_friendship()
        self.setup_schools()
        self.init_students()
        self.assign_jobs_and_wealth()
        self.setup_inactive_status()
        if self.unemployment_multiplier != "base":
            self.fix_unemployment(self.unemployment_multiplier)
        self.generate_households()
        self.setup_siblings()
        self.assing_parents()
        self.setup_employers_jobs()
        for agent in [a for a in self.schedule.agent_buffer(shuffled=True) if
                      a.my_job == None and a.my_school == None and a.age() >= 16 and a.age() < self.retirement_age
                      and a.job_level > 1]:
            agent.find_job()
        self.init_professional_links()
        self.calculate_crime_multiplier()
        self.calculate_criminal_tendency()
        self.calculate_arrest_rate()
        self.setup_oc_groups()
        self.setup_facilitators()
        for agent in self.schedule.agent_buffer(shuffled=True):
            agent.hobby = self.rng.integers(low = 1,high = 5, endpoint=True)
        self.calc_correction_for_non_facilitators()
        elapsed_time = time.time() - start
        hours = elapsed_time // 3600
        temp = elapsed_time - 3600 * hours
        minutes = temp // 60
        seconds = temp - 60 * minutes
        print("Setup Completed in: " + "%d:%d:%d" %(hours, minutes, seconds))

    def assign_jobs_and_wealth(self):
        """
        This procedure modifies the job_level and wealth_level attributes of agents in-place. This is just a first
        assignment, and will be modified first by the multiplier then by adding neet status.
        """
        for agent in self.schedule.agent_buffer(shuffled=True):
            if agent.age() > 16:
                agent.job_level = extra.pick_from_pair_list(self.work_status_by_edu_lvl[agent.education_level][agent.gender_is_male],self.rng)
                agent.wealth_level = extra.pick_from_pair_list(self.wealth_quintile_by_work_status[agent.job_level][agent.gender_is_male],self.rng)
            else:
                agent.job_level = 1
                agent.wealth_level = 1  #this will be updated by family membership

    def setup_inactive_status(self):
        """
        Based on labour_status_by_age_and_sex table, this method modifies the job_level attribute of the agents in-place.
        """
        for agent in self.schedule.agent_buffer(shuffled=True):
            if agent.age() > 14 and agent.age() < 65 and agent.job_level == 1 and self.rng.random() < \
                    self.labour_status_by_age_and_sex[agent.gender_is_male][agent.age()]:
                agent.job_level = 0

    def setup_employers_jobs(self):
        """
        Given a table this function generates the correct number of Jobs and Employers. Modify in-place the
        "my_employer" and "job_level" attributes of "Job" and the "my_jobs" attribute of "Employer".
        :return: None
        """
        self.job_counts = self.read_csv_city("employer_sizes").iloc[:, 0].values.tolist()
        # a small multiplier is added so to increase the pool to allow for matching at the job level
        self.jobs_target = len([a for a in self.schedule.agents if
                                a.job_level > 1 and a.my_school == None and a.age() > 16 and a.age() < self.retirement_age]) * 1.2
        while len(self.jobs) < self.jobs_target:
            n = self.rng.choice(self.job_counts, size=None)
            new_employer = Employer(self)
            self.employers.append(new_employer)
            for job in range(n):
                new_job = Job(self)
                self.jobs.append(new_job)
                new_job.my_employer = new_employer
                new_employer.my_jobs.append(new_job)
                new_job.job_level = self.random_level_by_size(n)

    def random_level_by_size(self, employer_size):
        """
        Given a float or int (employer_size) this function returns the level to be assigned
        based on the table (self.jobs_by_company_size) keys.
        :param employer_size: float,
        :return: int,
        """
        if employer_size in list(self.jobs_by_company_size.keys()):
            return extra.pick_from_pair_list(self.jobs_by_company_size[employer_size], self.rng)
        else:
            min_dist = 1e10
            for key in list(self.jobs_by_company_size.keys()):
                if abs(employer_size - key) < min_dist:
                    most_similar_key = key
                    min_dist = abs(employer_size - key)
            return extra.pick_from_pair_list(self.jobs_by_company_size[most_similar_key], self.rng)

    def init_professional_links(self):
        """
        Creates connections between agents within the same Employer.
        :return: None
        """
        for employer in self.employers:
            employees = employer.employees()
            conn = self.decide_conn_number(employees, 20)
            for employee in employees:
                total_pool = [agent for agent in employees if agent != employee]
                conn_pool = list(self.rng.choice(list(total_pool), conn, replace=False))
                employee.makeProfessionalLinks(conn_pool)

    def df_to_lists(self,df):
        """
        This function transforms a pandas DataFrame into nested lists as follows:
        df-columns = age, sex, education, p --> list = [[age,sex],[education,p]]

        This transformation ensures a faster access to the values using the position in the list
        :param df: pandas df, the df to be transformed
        :return: list, a new list
        """
        output_list = list()
        temp_list = df.iloc[:, :2].values.tolist()
        for index, row in df.iterrows():
            output_list.append([temp_list[index], [row.iloc[2], row.iloc[3]]])
        return output_list

    def calculate_crime_multiplier(self):
        """
        Based on self.c_range_by_age_and_sex this procedure modifies in-place the attribute self.crime_multiplier
        :return: None
        """
        total_crime = 0
        for line in self.c_range_by_age_and_sex:
            people_in_cell = [agent for agent in self.schedule.agents if
                              agent.age() > line[0][1] and agent.age() <= line[1][0] and agent.gender_is_male ==
                              line[0][0]]
            n_of_crimes = line[1][1] * len(people_in_cell)
            total_crime += n_of_crimes
        self.crime_multiplier = self.number_crimes_yearly_per10k / 10000 * self.initial_agents / total_crime

    def calculate_criminal_tendency(self):
        """
        Based on the c_range_by_age_and_sex distribution, this function calculates and assigns to each agent
        a value representing the criminal tendency. It modifies the attribute Person.criminal_tendency in-place.
        :return: None
        """
        for line in self.c_range_by_age_and_sex:
            #the line variable is composed as follows:
            #[[bool(gender_is_male), int(minimum age range)], [int(maximum age range), float(c value)]]
            subpop = [agent for agent in self.schedule.agents if
                      agent.age() >= line[0][1] and agent.age() <= line[1][0] and agent.gender_is_male == line[0][0]]
            if subpop:
                c = line[1][1]
                #c is the cell value. Now we calculate criminal-tendency with the factors.
                for agent in subpop:
                    agent.criminal_tendency = c
                    agent.update_criminal_tendency()
                #then derive the correction epsilon by solving $\sum_{i} ( c f_i + \epsilon ) = \sum_i c$
                epsilon = c - np.mean([agent.criminal_tendency for agent in subpop])
                for agent in subpop:
                    agent.criminal_tendency += epsilon
        if self.intervention_is_on() and self.facilitator_repression:
                self.calc_correction_for_non_facilitators()

    def calc_correction_for_non_facilitators(self):
        """
        This function modifies the self.correction_for_non_facilitators attribute of the model.
        :return: None
        """
        f = len([agent for agent in self.schedule.agents if agent.facilitator])
        n = len(self.schedule.agents)
        self.correction_for_non_facilitators = [
            (n - self.facilitator_repression_multiplier * f) / (n - f)] if f > 0 else 1.0

    def lognormal(self, mu, sigma):
        """
        Draw samples from a log-normal distribution
        :param mu: float, mean
        :param sigma: float, standard deviation
        :return: float, sample
        """
        return np.exp(mu + sigma * self.rng.normal())

    def calculate_arrest_rate(self):
        """
        This gives the base probability of arrest, proportionally to the number of expected crimes in the first year.
        Modifies the attribute self.arrest_rate in-place
        :return: None
        """
        self.arrest_rate = self.number_arrests_per_year / self.ticks_per_year / self.number_crimes_yearly_per10k / 10000 * self.initial_agents

    def assing_parents(self):
        """
        This function modifies in-place the Person.mother and Person.father attribute of agents, based on networks.
        :return: None
        """
        for agent in self.schedule.agents:
            if agent.neighbors.get("parent"):
                for parent in agent.neighbors.get("parent"):
                    if parent.gender_is_male:
                        agent.father = parent
                    else:
                        agent.mother = parent

    def choose_intervention_setting(self):
        """
        Selecting the intervention setting, modifies the model attributes in-place
        :return: None
        """
        if self.intervention == "baseline":
            self.family_intervention = None
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = False
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 12
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "preventive":
            self.family_intervention = "remove-if-OC-member"
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = False
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "preventive-strong":
            self.family_intervention = "remove-if-OC-member"
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = False
            self.targets_addressed_percent = 100
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "disruptive":
            self.family_intervention = None
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = False
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "disruptive-strong":
            self.family_intervention = None
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = True
            self.facilitator_repression = False
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "students":
            self.family_intervention = None
            self.social_support = "all"
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = False
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 12
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "students-strong":
            self.family_intervention = None
            self.social_support = "all"
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = False
            self.targets_addressed_percent = 100
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "facilitators":
            self.family_intervention = None
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = True
            self.facilitator_repression_multiplier = 3
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999

        if self.intervention == "facilitators-strong":
            self.family_intervention = None
            self.social_support = None
            self.welfare_support = None
            self.oc_boss_repression = False
            self.facilitator_repression = True
            self.facilitator_repression_multiplier = 20
            self.targets_addressed_percent = 10
            self.ticks_between_intervention = 1
            self.intervention_start = 13
            self.intervention_end = 9999


        # 778 / 1700
# next: testing an intervention that removes kids and then returning them.   
# test OC members formation

# next code, needed to run: social proximity

# next: repair the tests, stop pushing forward. Repair those tests!

# end class. From here, static methods

# warning: for now we don't load up the partner in the partner network
def conclude_wedding(ego, partner):
    for x in [ego, partner]:
        for y in x.neighbors["household"]:
            y.neighbors["household"].discard(x)  # should be remove(x) once we finish tests
    ego.neighbors["household"].add(partner)
    partner.neighbors["household"].add(ego)
    ego.neighbors["partner"].add(partner)
    partner.neighbors["partner"].add(ego)
staticmethod(conclude_wedding)

if __name__ == "__main__":

    model = MesaPROTON_OC()
    model.initial_agents = 100
    model.create_agents()
    num_co_offenders_dist = pd.read_csv(os.path.join(model.general_data, "num_co_offenders_dist.csv"))
    model.initial_agents = 200
    model.load_stats_tables()
    model.setup_education_levels()
    model.setup_persons_and_friendship()
    # Visualize network
    nx.draw(model.watts_strogatz)
    print("num links:")
    print(model.total_num_links())
    # model.setup_siblings()
    print("num links:")
    print(model.total_num_links())
