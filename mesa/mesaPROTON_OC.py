import extra
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np
import networkx as nx
from Person import *
from School import School
import timeit
# import testProton
from itertools import combinations
import os
from numpy.random import default_rng

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
        self.this_is_a_big_crime = 0
        self.good_guy_threshold = 0
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
        self.jobs_by_company_size = 0
        self.education_levels = dict()  # table from education level to data
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
        self.schools = list()

        self.schedule = RandomActivation(self)

        # from graphical interface
        self.initial_agents = 100
        self.max_accomplice_radius = 2
        self.number_arrests_per_year = 30
        self.ticks_per_year = 12
        self.number_crimes_yearly_per10k = 2000
        self.ticks = 0
        self.num_oc_persons = 30
        self.num_oc_families = 8
        self.education_modifier = 1.0 #education-rate in Netlogo model
        self.retirement_age = 65

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
        # self.datacollector = DataCollector(
        #     model_reporters={"Gini": compute_gini},
        #     agent_reporters={"Wealth": "wealth"}
        # )
        # this gives the base probability of arrest, propotionally to the number of expected crimes in the first year.
        self.arrest_rate = self.number_arrests_per_year / self.ticks_per_year / self.number_crimes_yearly_per10k / 10000 * self.initial_agents

        # Create agents(
        # mesaConfigCreateAgents.configAgents(self)
        # print(MesaFin4.creation_frequency)
        # self.running = True
        # self.datacollector.collect(self)

    def create_agents(self, random_relationships=False):
        for i_agent in range(0, self.initial_agents):
            i_agent = Person(self)
            self.schedule.add(i_agent)
            i_agent.random_init(random_relationships)

    def step(self):
        self.schedule.step()
        self.wedding()
        # collect data
        # self.datacollector.collect(self)

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
        for x in self.schedule.agents:
            x.facilitator = True if not x.oc_member and x.age() > 18 and (self.rng.uniform(0, 1) < self.percentage_of_facilitators) else False

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
        self.work_status_by_edu_lvl = self.read_csv_city("work_status_by_edu_lvl")
        self.wealth_quintile_by_work_status = self.read_csv_city("wealth_quintile_by_work_status")
        self.punishment_length_list = self.read_csv_city("conviction_length")
        # male_punishment_length_list =  map [ i _> (list (item 0 i) (item 2 i)) ] punishment_length_list
        # female_punishment_length_list =  map [ i _> (list (item 0 i) (item 1 i)) ] punishment_length_list
        self.jobs_by_company_size = self.read_csv_city("jobs_by_company_size")
        self.c_range_by_age_and_sex = self.read_csv_city("crime_rate_by_gender_and_age_range")
        self.c_by_age_and_sex = self.read_csv_city("crime_rate_by_gender_and_age")
        self.labour_status_by_age_and_sex = self.read_csv_city("labour_status")
        self.labour_status_range = self.read_csv_city("labour_status_range")
        # further sources:
        # schools.csv table goes into education_levels
        marriage = pd.read_csv(os.path.join(self.general_data, "marriages_stats.csv"))
        self.number_weddings_mean = marriage['mean_marriages'][0]
        self.number_weddings_sd = marriage['std_marriages'][0]

    def wedding(self):
        corrected_weddings_mean = (self.number_weddings_mean * len(self.schedule.agents) / 1000) / 12
        num_wedding_this_month = self.rng.poisson(corrected_weddings_mean)  # if num-wedding-this-month < 0 [ set num-wedding-this-month 0 ] ???
        maritable = [x for x in self.schedule.agents if x.age() > 25 and x.age() < 55 and x.partner == None]
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
                                           size=1,
                                           replace=False)[0]
                conclude_wedding(ego, partner)
                maritable.remove(partner)
                num_wedding_this_month -= 1
                self.number_weddings += 1
            maritable.remove(ego)  # removed in both cases, if married or if can't find a partner

    def intervention_on(self):
        return self.ticks % self.ticks_between_intervention == 0 and \
               self.ticks >= intervention_start and \
               self.ticks < intervention_end

    def socialization_intervene(self):
        potential_targets = [x for x in schedule.agents if x.age() < 18 and x.age >= 6 and x.my_school != None]
        targets = self.rng.choice(potential_targets,
                                   p=[x.criminal_tendency for x in potential_targets],
                                   size=math.ceil((targets_addressed_percent / 100 * len(potential_targets))
                                                  # criminal_tendency + criminal_tendency_addme_for_weighted_extraction
                                                  )
                                   )
        if social_support == "educational" or social_support == "all": self.soc_add_educational(targets)
        if social_support == "psychological" or social_support == "all": self.soc_add_psychological(targets)
        if social_support == "more friends" or social_support == "all": self.soc_add_more_friends(targets)
        welfare_createjobs({x for x in schedule.agents if
                            x.gender_is_male == False and x.neighbors.get('offspring').intersection(set(targets))})

    def soc_add_educational(self, targets):
        for x in targets: x.max_education_level = min(max_education_level + 1, max(education_levels.keys()))

    def soc_add_psychological(self, targets):
        # we use a random sample (arbitrarily to =  50 people size max) to avoid weighting sample from large populations
        for x in targets:
            support_set = extra.at_most(50, [y for y in schedule.agents if y.num_crimes_committed == 0 and y.age() > x.age()], self.rng)
        if support_set:
            chosen = self.rng.choice(support_set,
                                      p=[(1 - (y.age() - x.age()) / 120) for y in support_set],
                                      size=1,
                                      replace=False)[0]
            chosen.makeFriends(x)

    def soc_add_more_friends(self, targets):
        for x in targets:
            support_set = limited.extraction(schedule.agents.remove(x))
            if support_set:
                x.makeFriends(self.rng.choice(support_set, size=1,
                                             p=[self.criminal_tendency_subtractfromme_for_inverse_weighted_extraction
                                                - y.criminal_tendency for y in support_set]))

    def welfare_intervene(self):
        if welfare_support == "job_mother":
            targets = [x for x in schedule.agents if
                       x.gender_is_male == False and
                       not x.my_job and
                       (True if not x.partner else not x.partner.oc_member)
                       ]
        if welfare_support == "job_child":
            targets = [x for x in schedule.agents if
                       x.age() > 16 and x.age() < 24 and
                       not x.my_school and
                       not x.my_job and
                       x.father.oc_member
                       ]
        if targets:
            targets = self.rng.choice(targets, math.ceil(targets_addressed_percent / 100 * len(targets)), replace=False)
            self.welfare_createjobs(targets)

    def welfare_createjobs(self, targets):
        for x in targets:
            the_employer = self.rng.choice(self.employers)
            the_level = x.job_level if x.job_level >= 2 else 2
            the_employer.create_job(the_level, x)
            for y in extra.at_most(20, the_employer.employees, self.rng):
                x.makeProfessionalLinks(y)

    # here I have to decide how to manage father and mother links. Just as pointers? Then how do I collapse them into the family network?
    # for now I think I'll just add another network and keep the redundancy, then we'll see.
    def family_intervene(self):
        kids_to_protect = [x for x in schedule.agents if x.age_between(12, 18)]
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
            for x in self.rng.choice(kids_to_protect, how_many, replace=False):
                kids_intervention_counter += 1
                # this also removes household links, leaving the household in an incoherent state.
                x.neighbor.get('parent').remove(x.father)
                # maybe not needed?
                self.removed_fatherships.add([((18 * ticks_per_year + birth_tick) - ticks), x.father, x])
                # at this point bad dad is out and we help the remaining with the whole package
                family = x.family().add(x)
                self.welfare_createjobs([y for y in family if y.age() >= 16 and not y.job and not y.my_school])
                self.soc_add_educational([y for y in family if y.age() < 18 and not y.job])
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
        for a in self.schedule.agents:
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
        # OC members are scaled down if we don't have 10K agents
        scaled_num_oc_families = math.ceil(
            self.num_oc_families * self.initial_agents / 10000 * self.num_oc_persons / 30)
        scaled_num_oc_persons = math.ceil(self.num_oc_persons * self.initial_agents / 10000)
        # families first. Note that it could extract the same family twice. This could be improved to force exactly the number of families needed.
        # we assume here that we'll never get a negative criminal tendency.
        oc_family_head = extra.weighted_n_of(scaled_num_oc_families,
                                             self.schedule.agents, lambda x: x.criminal_tendency, self.rng)
        for x in oc_family_head: x.oc_member = True
        candidates_in_families = [y for y in x.neighbors.get('household') if y.age() >= 18 for x in oc_family_head]
        if len(candidates_in_families) >= scaled_num_oc_persons - scaled_num_oc_families:  # family members will be enough
            members_in_families = extra.weighted_n_of(scaled_num_oc_persons - scaled_num_oc_families,
                                                      candidates_in_families, lambda x: x.criminal_tendency, self.rng)
            # fill up the families as much as possible
            for z in members_in_families: z.oc_member = True
        else:  # take more as needed (note that this modifies the count of families)
            for z in candidates_in_families: z.oc_member = True
            non_oc = [z for z in self.schedule.agents if not z.oc_member]
            extras = extra.weighted_n_of(scaled_num_oc_persons - len(candidates_in_families) - len(oc_family_head),
                                         non_oc, lambda x: x.criminal_tendency, self.rng)
            for x in extras: x.oc_member = True
        # and now, the network with its weights..
        oc_members = [x for x in self.schedule.agents if x.oc_member]
        for (i, j) in combinations(oc_members, 2): i.addCriminalLink(j)

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

    def incestuos(self, ego, candidates):
        all_potential_siblings = [ego] + candidates + list(ego.neighbors.get('sibling')) + [s for c in candidates for s
                                                                                            in
                                                                                            c.neighbors.get('sibling')]
        return ego.partner in all_potential_siblings

    def setup_siblings(self):
        for p in [p for p in self.schedule.agents if
                  p.neighbors.get('parent')]:  # simulates people who left the original household.
            num_siblings = self.rng.poisson(0.5)  # 0.5 -> the number of links is N^3 agents, so let's keep this low
            # at this stage links with other persons are only relatives inside households and friends.
            candidates = [c for c in self.schedule.agents if
                          c.neighbors.get('parent') and not p.isneighbor(c) and abs(p.age() - c.age()) < 5]
            candidates = [c for c in self.schedule.agents if not p.isneighbor(c) and abs(p.age() - c.age()) < 5]
            candidates = self.rng.choice(candidates, min(len(candidates), 5), False).tolist()
            print("len cand:" + str(len(candidates)))
            # remove couples from candidates and their neighborhoods
            while len(candidates) > 0 and not self.incestuos(p, candidates):
                # trouble should exist, or incestous would be false.
                trouble = self.rng.choice(
                    [x for x in candidates if x.partner], 1).tolist()
                candidates = cadidates.remove(trouble)
            targets = p + self.rng.choice(candidates,
                                           min(len(candidates, num_siblings))
                                           )
            targets = targets + set([x.neighbors.get("siblings") for x in targets])
            for x in targets:
                x.addSiblingLinks(p)

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

    def df_to_dict(self, df):
        """
        Based on the size of the dataframe, it transforms the dataframe into a nested dictionary.
        :param df: pandas dataframe
        :return: dic
        """
        dic = dict()
        if len(df.columns) == 2:
            for col in np.unique(df.iloc[:,0]):
                dic[col] = float(df[df.iloc[:,0] == col].iloc[:,1].values)
        if len(df.columns) == 3:
            for col in np.unique(df.iloc[:,0]):
                dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1:].values
        if len(df.columns) == 4:
            for col in np.unique(df.iloc[:, 0]):
                dic[col] = df[df.iloc[:, 0] == col].iloc[:, 1:]
            for key in dic:
                subdic = dict()
                for subcol in np.unique(dic[key].iloc[:, 0]):
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
                conn_pool = list(self.rng.choice(list(total_pool), conn, replace=False))
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
        Warning: At the moment this procedure is partial, it has been added for testing in the development phase.
        Standard setup of the model
        :param n_agent: int, number of initial agents
        """
        self.initial_agents = n_agent
        self.setup_education_levels()
        self.setup_persons_and_friendship()
        self.setup_schools()
        self.init_students()




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
    ego.neighbors["household"] = {partner}
    partner.neighbors["household"] = {ego}
    ego.partner = partner
    partner.partner = ego
staticmethod(conclude_wedding)


if __name__ == "__main__":

    m = MesaPROTON_OC()
    m.initial_agents = 100
    m.create_agents()
    num_co_offenders_dist = pd.read_csv(os.path.join(m.general_data, "num_co_offenders_dist.csv"))
    m.initial_agents = 200
    m.load_stats_tables()
    m.setup_education_levels()
    m.setup_persons_and_friendship()
    # Visualize network
    nx.draw(m.watts_strogatz)
    print("num links:")
    print(m.total_num_links())
    # m.setup_siblings()
    print("num links:")
    print(m.total_num_links())



