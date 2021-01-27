# MIT License
#
# Copyright (c) 2019 Mario Paolucci
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from __future__ import annotations
import os
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np
import networkx as nx
from tqdm import tqdm
from itertools import combinations, chain
from numpy.random import default_rng
import time
from entities import Person, School, Employer, Job
import extra
from typing import List, Set, Union, Dict


class ProtonOC(Model):
    """
    Simulation of recruitment to terrorism.
    Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu
    """

    def __init__(self, seed: int = int(time.time())) -> None:
        super().__init__(seed=seed)
        self.seed: int = seed
        self.rng: np.random.default_rng = default_rng(seed)
        self.verbose: bool = False
        self.check_random: List[float] = [self.rng.random(), self.random.random()]
        self.education_levels: Dict = dict()  # table from education level to data
        self.removed_fatherships: list = list()
        self.schools: List[School] = list()
        self.jobs: List[Job] = list()
        self.employers: List[Employer] = list()
        self.datacollector: Union[DataCollector, None] = None
        self.meta_graph: nx.Graph = nx.Graph()

        # Intervention
        self.family_intervention: Union[str, None] = None
        self.social_support: Union[str, None] = None
        self.welfare_support: Union[str, None] = None

        # outputs
        self.this_is_a_big_crime: int = 3
        self.good_guy_threshold: float = 0.6
        self.number_deceased: float = 0
        self.facilitator_fails: float = 0
        self.facilitator_crimes: float = 0
        self.crime_size_fails: float = 0
        self.number_born: int = 0
        self.number_migrants: int = 0
        self.number_weddings: int = 0
        self.number_weddings_mean: float = 100
        self.number_weddings_sd: float = 0
        self.number_law_interventions_this_tick: int = 0
        self.correction_for_non_facilitators: float = 0
        self.number_protected_recruited_this_tick: int = 0
        self.number_offspring_recruited_this_tick: int = 0
        self.people_jailed: int = 0
        self.number_crimes: int = 0
        self.crime_multiplier: float = 0
        self.kids_intervention_counter: int = 0
        self.big_crime_from_small_fish: int = 0  # checking anomalous crimes
        self.families: List = list()
        self.hh_size: List = list()
        self.arrest_rate: Union[int, float] = 0

        #Scheduler
        self.schedule: RandomActivation = RandomActivation(self)

        # from graphical interface
        self.migration_on: bool = False
        self.initial_agents: int = 100
        self.intervention: str = "baseline"
        self.max_accomplice_radius: int = 2
        self.number_arrests_per_year: int = 30
        self.ticks_per_year: int = 12
        self.number_crimes_yearly_per10k: int = 2000
        self.ticks: int = 0
        self.ticks_between_intervention: int = 1
        self.intervention_start: int = 13
        self.intervention_end: int = 999
        self.num_oc_persons: int = 30
        self.num_oc_families: int = 8
        self.education_modifier: float = 1.0  # education-rate in Netlogo model
        self.retirement_age: int = 65
        self.unemployment_multiplier: Union[str, int] = "base"
        self.nat_propensity_m: float = 1.0
        self.nat_propensity_sigma: float = 0.25
        self.nat_propensity_threshold: float = 1.0
        self.facilitator_repression: bool = False
        self.facilitator_repression_multiplier: float = 2.0
        self.likelihood_of_facilitators: float = 0.005
        self.targets_addressed_percent: float = 10
        self.threshold_use_facilitators: float = 4
        self.oc_embeddedness_radius: int = 2
        self.oc_boss_repression: bool = False
        self.punishment_length: int = 1
        self.constant_population: bool = False

        # Folders definition
        self.mesa_dir: str = os.getcwd()
        self.cwd: str = os.path.dirname(self.mesa_dir)
        self.input_directory: str = os.path.join(self.cwd, "inputs")
        self.palermo: str = os.path.join(self.input_directory, "palermo")
        self.eindhoven: str = os.path.join(self.input_directory, "eindhoven")
        self.general: str = os.path.join(self.input_directory, "general")
        self.general_data: str = os.path.join(self.general, "data")
        self.data_folder: str = os.path.join(self.palermo, "data")
        """
        Directory structure:
        ├───inputs (@self.input_directory)
        │   ├───eindhoven (@self.eindhoven)
        │   │   ├───data
        │   │   └───raw
        │   ├───general (@self.general)
        │   │   ├───data
        │   │   └───raw
        │   └───palermo (@self.palermo_inputs)
        │       ├───data
        │       └───raw
        generated with github.com/nfriend/tree-online
        """
        # Load tables
        self.fertility_table = extra.df_to_dict(
            self.read_csv_city("initial_fertility_rates"), extra_depth=True)
        self.mortality_table = extra.df_to_dict(
            self.read_csv_city("initial_mortality_rates"), extra_depth=True)
        self.edu = extra.df_to_dict(self.read_csv_city("edu"))
        self.age_gender_dist = self.read_csv_city("initial_age_gender_dist").values.tolist()
        self.edu_by_wealth_lvl = self.read_csv_city("edu_by_wealth_lvl")
        self.work_status_by_edu_lvl = extra.df_to_dict(
            self.read_csv_city("work_status_by_edu_lvl"))
        self.wealth_quintile_by_work_status = extra.df_to_dict(
            self.read_csv_city("wealth_quintile_by_work_status"))
        self.punishment_length_data = self.read_csv_city("conviction_length")
        self.male_punishment_length = extra.df_to_lists(
            self.punishment_length_data[["months", "M"]], split_row=False)
        self.female_punishment_length = extra.df_to_lists(
            self.punishment_length_data[["months", "F"]], split_row=False)
        self.jobs_by_company_size = extra.df_to_dict(
            self.read_csv_city("jobs_by_company_size"))
        self.c_range_by_age_and_sex = extra.df_to_lists(
            self.read_csv_city("crime_rate_by_gender_and_age_range"))
        self.c_by_age_and_sex = self.read_csv_city("crime_rate_by_gender_and_age")
        self.labour_status_by_age_and_sex = extra.df_to_dict(
            self.read_csv_city("labour_status"), extra_depth=True)
        self.labour_status_range = extra.df_to_dict(
            self.read_csv_city("labour_status_range"), extra_depth=True)
        marriage = pd.read_csv(os.path.join(
            self.general_data, "marriages_stats.csv"))
        self.number_weddings_mean = marriage['mean_marriages'][0]
        self.number_weddings_sd = marriage['std_marriages'][0]
        self.num_co_offenders_dist = extra.df_to_lists(
            pd.read_csv(os.path.join(
                self.general_data, "num_co_offenders_dist.csv")), split_row=False)
        self.head_age_dist = extra.df_to_dict(
            self.read_csv_city("head_age_dist_by_household_size"))
        self.proportion_of_male_singles_by_age = extra.df_to_dict(
            self.read_csv_city("proportion_of_male_singles_by_age"))
        self.hh_type_dist = extra.df_to_dict(
            self.read_csv_city("household_type_dist_by_age"))
        self.partner_age_dist = extra.df_to_dict(
            self.read_csv_city("partner_age_dist"))
        self.children_age_dist = extra.df_to_dict(
            self.read_csv_city("children_age_dist"))
        self.p_single_father = self.read_csv_city("proportion_single_fathers")
        self.job_counts = self.read_csv_city("employer_sizes").iloc[:, 0].values.tolist()


    def __repr__(self):
        return "PROTON-OC MODEL, seed: " + str(self.seed)


    def init_collector(self, complete: bool = False) -> None:
        """
        This function instantiates a mesa.datacollection.DataCollector object. This object allows
        to collect the data generated by the model. It is accessed at the end of the setup and at
        the end of each step, all attributes of the model and all attributes of all agents are
        collected each call. If complete is True, additional information are collected that need
        to be calculated and therefore may slow down the model (e.g. oc_embeddedness that call the
        function Person.oc_embeddedness()) The collected data is stored in a dictionary and
        transformed into a Dataframe when get_model_vars_dataframe() or get_agents_vars_dataframe()
        are called.
        :param complete: bool, if True extra data are collected
        :return: None
        """
        model_reporters = {key: key for key in self.__dict__.keys()}
        agent_reporters = {key: key for key in self.schedule.agents[0].__dict__.keys()}
        if complete:
            agent_reporters["oc_embeddedness"] = lambda x: x.oc_embeddedness()
        self.datacollector = DataCollector(model_reporters=model_reporters,
                                           agent_reporters=agent_reporters)


    def step(self) -> None:
        """
        This procedure is the step or rather a single tick of the model. The mesa package is
        designed so that the step function of the model should activate the step function of
        individual agents through the scheduler. In this model on the contrary agents do not
        have a step function (or rather they do but it does nothing), everything is managed
        by the step function of the model.

        :return: None
        """
        for agent in self.schedule.agents:
            agent.num_crimes_committed_this_tick = 0
            agent.calculate_age()
        self.number_law_interventions_this_tick = 0
        if self.intervention_is_on():
            if self.family_intervention:
                self.family_intervene()
            if self.social_support:
                self.socialization_intervene()
            if self.welfare_support:
                self.welfare_intervene()
            # OC-members-repression works in arrest-probability-with-intervention in commmit-crime
        if (self.ticks % self.ticks_per_year) == 0:
            self.calculate_criminal_tendency()
            self.calculate_crime_multiplier()  # we should update it, if population change
            self.graduate_and_enter_jobmarket()
            # updates neet status only when changing age range (the age is a key of the table)
            for agent in [agent for agent in self.schedule.agents
                          if agent.job_level < 2 and agent.just_changed_age() and
                          agent.age in self.labour_status_range[agent.gender_is_male].keys()]:
                agent.update_unemployment_status()
            for agent in [agent for agent in self.schedule.agents
                          if not agent.my_school and 18 <= agent.age < self.retirement_age
                          and not agent.my_job and not agent.retired and agent.job_level > 1]:
                agent.find_job()
                if agent.my_job:
                    total_pool = [candidate for candidate in agent.my_job.my_employer.employees()
                                  if candidate != agent]
                    employees = list(
                        self.rng.choice(total_pool, extra.decide_conn_number(total_pool, 20,
                                                                             also_me=False),
                                        replace=False))
                    agent.make_professional_link(employees)
            self.let_migrants_in()
            self.return_kids()
        self.wedding()
        self.reset_oc_embeddedness()
        self.commit_crimes()
        self.retire_persons()
        self.make_baby()
        self.remove_excess_friends()
        self.remove_excess_professional_links()
        self.make_friends()
        for agent in self.schedule.agents:
            if agent.prisoner:
                agent.sentence_countdown -= 1
                if agent.sentence_countdown == 0:
                    agent.prisoner = False
        self.make_people_die()
        self.datacollector.collect(self)
        self.schedule.step()
        self.ticks += 1


    def run(self, n_agents: int, ticks: int, verbose: bool = False) -> None:
        """
        Run the model setup with @n_agents agents and execute @ticks tick.

        :param n_agents: int, number of agents
        :param ticks:int, number of agents
        :param verbose: bool, extended console printing
        :return:
        """
        self.verbose = verbose
        self.setup(n_agents)
        pbar = tqdm(np.arange(0, ticks))
        for tick in pbar:
            self.step()
            pbar.set_description("tick: %s" % tick)


    def fix_unemployment(self, correction: Union[float, int, str]) -> None:
        """
        Applies a correction to the employment level, with a correction > 1 increase unemployment
        otherwise decrease unemployment. This policy is applied by modifying in-place the
        Person.job_level attribute of the eligible agents
        :param correction: Union[float, int, str], the correction
        :return: None
        """
        available = [agent for agent in self.schedule.agents if 16 < agent.age < 65
                     and agent.my_school is None]
        unemployed = [agent for agent in available if agent.job_level == 1]
        occupied = [agent for agent in available if agent.job_level > 1]
        notlooking = [agent for agent in available if agent.job_level == 0]
        ratio_on = len(occupied) / (len(occupied) + len(notlooking))
        if correction > 1:
            # increase unemployment
            for x in self.rng.choice(occupied, int(((correction - 1) * len(unemployed) *
                                                    ratio_on)),
                                     replace=False):
                x.job_level = 1  # no need to resciss job links as they haven't been created yet.
            for x in self.rng.choice(notlooking, int((correction - 1) * len(unemployed) *
                                                     (1 - ratio_on)),
                                     replace=False):
                x.job_level = 1  # no need to resciss job links as they haven't been created yet.
        else:
            # decrease unemployment
            for x in self.rng.choice(unemployed, int((1 - correction) * len(unemployed)),
                                     replace=False):
                x.job_level = 2 if self.rng.uniform(0, 1) < ratio_on else 0


    def setup_facilitators(self) -> None:
        """
        Based on parameter ProtonOc.percentage_of_facilitators this function gives a number of
        agents to become facilitators, modifying the Person.facilitator attribute in-place.

        :return: None
        """
        for agent in self.schedule.agent_buffer(shuffled=True):
            agent.facilitator = True if not agent.oc_member and agent.age > 18 and (self.rng.uniform(0, 1) < self.likelihood_of_facilitators) else False


    def read_csv_city(self, filename: str) -> pd.DataFrame:
        """
        Based on the ProtonOc.data_folder attribute, which represents the directory of the city
        of interest, this function returns a pd.DataFrame named filename in the directory. Warning,
        the file must be a .csv file, it is not necessary to pass also the extension

        :param filename: str, the filename
        :return: pd.DataFrame, a pandas dataframe
        """
        return pd.read_csv(os.path.join(self.data_folder, filename + ".csv"))


    def wedding(self) -> None:
        """
        This procedure allows eligible agents (age > 25 and < 55 without any partner) to get
        married and thus create a new household.
        :return: None
        """
        corrected_weddings_mean = (self.number_weddings_mean *
                                   len(self.schedule.agents) / 1000) / 12
        num_wedding_this_month = self.rng.poisson(corrected_weddings_mean)
        marriable = [agent for agent in self.schedule.agents if 25 < agent.age < 55
                     and not agent.neighbors.get("partner")]
        while num_wedding_this_month > 0 and len(marriable) > 1:
            ego = self.rng.choice(marriable)
            poolf = ego.neighbors_range("friendship",
                                        self.max_accomplice_radius) & set(marriable)
            poolp = ego.neighbors_range("professional",
                                        self.max_accomplice_radius) & set(marriable)
            pool = [agent for agent in (poolp | poolf) if
                    agent.gender_is_male != ego.gender_is_male and
                    (agent.age - ego.age) < 8 and
                    agent not in ego.neighbors.get("sibling") and
                    agent not in ego.neighbors.get("offspring") and
                    ego not in agent.neighbors.get("offspring")]  # directed network
            if pool:  # TODO: add link to Netlogo2Mesa
                partner = self.rng.choice(pool, p=extra.wedding_proximity_with(ego, pool))
                for agent in [ego, partner]:
                    agent.remove_from_household()
                ego.neighbors.get("household").add(partner)
                partner.neighbors.get("household").add(ego)
                ego.neighbors.get("partner").add(partner)
                partner.neighbors.get("partner").add(ego)
                marriable.remove(partner)
                num_wedding_this_month -= 1
                self.number_weddings += 1
            marriable.remove(ego)  # removed in both cases, if married or if can't find a partner


    def socialization_intervene(self) -> None:
        """
        This procedure is active when the self.social_support attribute is different from None.
        There are 4 possible social interventions: educational, psychological, more-friends or all.
        The intervention has effect on a portion of eligible members, determined by @how_many
        variable that depends on self.targets_addressed_percent attribute.
        The interventions consist of:
        1. soc_add_educational, the max_education_level attribute of the eligible members is
        increased by one
        2. soc_add_psychological, a new support member (who has not committed crimes) is added
        to the friends network
        3. soc_add_more_friends, a new support member (with a low level of tendency to crime)
        is added to the friends network
        4. welfare_createjobs, new jobs are created and assigned to eligible members (mothers)

        :return: None
        """
        potential_targets = [agent for agent in self.schedule.agents if
                             agent.age <= 18 >= 6 and agent.my_school is not None]
        how_many = int(np.ceil(self.targets_addressed_percent / 100 * len(potential_targets)))
        targets = extra.weighted_n_of(how_many, potential_targets,
                                      lambda x: x.criminal_tendency,
                                      self.rng)
        if self.social_support == "educational" or self.social_support == "all":
            self.soc_add_educational(targets)
        if self.social_support == "psychological" or self.social_support == "all":
            self.soc_add_psychological(targets)
        if self.social_support == "more-friends" or self.social_support == "all":
            self.soc_add_more_friends(targets)
        # also give a job to the mothers
        if self.social_support == "all":
            self.welfare_createjobs([agent.mother for agent in self.schedule.agents
                                     if agent.mother])


    def soc_add_educational(self, targets: Union[List[Person], Set[Person]]) -> None:
        """
        This procedure modifies the Person.max_education_level attribute of targets in-place,
        by adding +1 if possible. This method is activated by ProtonOc.socialization_intervene()

        :param targets: Union[List[Person], Set[Person], the target
        :return: None
        """
        for agent in targets:
            agent.max_education_level = min(agent.max_education_level + 1,
                                            max(self.education_levels.keys()))


    def soc_add_psychological(self, targets: Union[List[Person], Set[Person]]) -> None:
        """
        For each target a new support member (who has not committed crimes) is added to the
        friends network. This method is activated by ProtonOc.socialization_intervene()
        :param targets: Union[List[Person], Set[Person], the target
        :return: None
        """
        # we use a random sample (arbitrarily to =  50 people size max) to avoid weighting sample
        # from large populations
        for agent in targets:
            support_set = extra.at_most([support_agent for support_agent in self.schedule.agents if
                                         support_agent.num_crimes_committed == 0
                                         and support_agent.age > agent.age and
                                         support_agent != agent], 50, self.rng)
            if support_set:
                chosen = extra.weighted_one_of(support_set,
                                               lambda x: 1 - abs((x.age - agent.age) / 120),
                                               self.rng)
                chosen.make_friendship_link(agent)


    def soc_add_more_friends(self, targets: Union[List[Person], Set[Person]]) -> None:
        """
        For each target a new friend (with a low level of Person.criminal_tendency) is added to the
        friends network
        :param targets: Union[List[Person], Set[Person], the target
        :return: None
        """
        # todo: calculate max_criminal_tendency could be expensive  Maybe we should only
        #  recalculate it when criminal tendency changes?
        max_criminal_tendency = max([0] + [agent.criminal_tendency for agent in self.schedule.agents])
        for target in targets:
            support_set = extra.at_most([agent for
                                        agent in self.schedule.agents if agent != target],
                                        50, self.rng)
            if support_set:
                target.make_friendship_link(
                    extra.weighted_one_of(support_set,
                                          lambda x: max_criminal_tendency - x.criminal_tendency,
                                          self.rng))


    def welfare_intervene(self) -> None:
        """
        This procedure is active when the self.welfare_support attribute is different from None.
        There are 2 possible welfare interventions determined by the parameter
        ProtonOc.welfare_support: job-mother or job-child. These parameters determine the portion
        of the population on which the intervention will have effect. The intervention consists of
        the application of a single procedures on eligible family members:
        1. new jobs are created and assigned to eligible members (mothers or children)

        :return: None
        """
        targets = list()
        if self.welfare_support == "job-mother":
            for mother in [agent.mother for agent in self.schedule.agents if agent.mother]:
                if not mother.my_job and mother.neighbors.get("partner"):
                    if mother.get_neighbor_list("partner")[0].oc_member:
                        targets.append(mother)
        if self.welfare_support == "job-child":
            for agent in self.schedule.agents:
                if 16 < agent.age < 24 and not agent.my_school \
                        and not agent.my_job and agent.father:
                    if agent.father.oc_member:
                        targets.append(agent)
        if targets:
            how_many = np.ceil(self.targets_addressed_percent / 100 * len(targets))
            targets = self.rng.choice(targets, how_many, replace=False)
            self.welfare_createjobs(targets)


    def welfare_createjobs(self, targets: Union[List[Person], Set[Person]]) -> None:
        """
        This procedure creates new jobs for each member within targets.
        :param targets: Union[List[Person], Set[Person]], the target
        :return: None
        """
        for agent in targets:
            the_employer = self.rng.choice(self.employers)
            the_level = agent.job_level if agent.job_level >= 2 else 2
            the_employer.create_job(the_level, agent)
            for new_professional_link in extra.at_most(the_employer.employees(), 20, self.rng):
                agent.make_professional_link(new_professional_link)


    def family_intervene(self) -> None:
        """
        This procedure is active when the self.family_intervention attribute is different from None
        There are 3 possible family interventions: remove_if_caught, remove_if_OC_member and
        remove_if_caught_and_OC_member. These parameters determine the portion of the population on
        which the intervention will have effect. The intervention consists of the application of 5
        procedures on eligible family members:
        1. Fathers who comply with the conditions are removed from their families  (Removed fathers
        are stored within the removed_fatherships attribute so it is possible at any time to
        reintroduce them into the family.)
        2. welfare_createjobs, new jobs are created and assigned to eligible members.
        3. soc_add_educational, the max_education_level attribute of the eligible members is
        increased by one
        4. soc_add_psychological, a new support member (who has not committed crimes) is added
        to the friends network
        5. soc_add_more_friends, a new support member (with a low level of tendency to crime)
        is added to the friends network
        :return: None
        """
        kids_to_protect = [agent for agent in self.schedule.agents if
                           12 <= agent.age < 18 and agent.father in agent.neighbors.get("parent")]
        if self.family_intervention == "remove-if-caught":
            kids_to_protect = [agent for agent in kids_to_protect if agent.father.prisoner]
        if self.family_intervention == "remove-if-OC-member":
            kids_to_protect = [agent for agent in kids_to_protect if agent.father.oc_member]
        if self.family_intervention == "remove-if-caught-and-OC-member":
            kids_to_protect = [agent for agent in kids_to_protect if
                               agent.father.prisoner and agent.father.oc_member]
        if kids_to_protect:
            how_many = int(np.ceil(self.targets_addressed_percent / 100 * len(kids_to_protect)))
            kids_pool = list(self.rng.choice(kids_to_protect, how_many, replace=False))
            for kid in kids_pool:
                self.kids_intervention_counter += 1
                # notice that the intervention acts on ALL family members respecting the condition,
                # causing double
                # calls for families with double targets.
                # gee but how comes that it increases with the nubmer of targets?
                # We have to do better here
                # this also removes household links, leaving the household in an incoherent state.
                kid.neighbors.get("parent").remove(kid.father)
                kid.father.neighbors.get("offspring").remove(kid)
                self.removed_fatherships.append([((18 * self.ticks_per_year + kid.birth_tick) - self.ticks), kid.father, kid])
                # we do not modify Person.father, this attribute is implemented so that it is possible to remove the father from the network and keep the information.
                # at this point bad dad is out and we help the remaining with the whole package
                # family_links_neighbors also include siblings that could be assigned during
                # setup through the
                # setup_siblings procedure,
                # we do not need these in this procedure
                family = [kid] + kid.family_link_neighbors()
                self.welfare_createjobs(
                    [agent for agent in family if agent.age >= 16
                     and not agent.my_job and not agent.my_school])
                self.soc_add_educational([agent for agent in family if agent.age < 18
                                          and not agent.my_job])
                self.soc_add_psychological(family)
                self.soc_add_more_friends(family)


    def return_kids(self) -> None:
        """
        If the conditions are respected, this procedure allows fathers to return to the household.
        This procedure is closely related to procedure ProtonOc.family_intervene()
        :return: None
        """
        if self.removed_fatherships:
            for removed in self.removed_fatherships:
                if removed[2].age >= 18 and self.rng.random() < 6 / removed[0]:
                    removed[2].neighbors.get("parent").add(removed[2].father)
                    removed[2].father.neighbors.get("offspring").add(removed[2])
                    self.removed_fatherships.remove(removed)


    def make_friends(self) -> None:
        """
        This procedure allows agents to make new friends, based on extra.social proximity().
        Is activated at every tick.
        :return: None
        """
        for agent in self.schedule.agent_buffer(shuffled=True):
            p_friends = agent.potential_friends()
            if len(p_friends) > 0:
                friends = extra.weighted_n_of(np.min([len(p_friends), self.rng.poisson(3)]),
                                              p_friends,
                                              lambda x: extra.social_proximity(agent, x),
                                              self.rng)
                for chosen in friends:
                    chosen.make_friendship_link(agent)


    def remove_excess_friends(self) -> None:
        """
        Given the dunbar number this procedure cut the excess friendship links. Is activated at
        every tick. Source: Dunbar, R. I. (1993). Coevolution of neocortical size,  group size and
        language in humans. Behavioral and brain sciences, 16(4), 681-694.
        :return: None
        """
        for agent in self.schedule.agents:
            friends = agent.neighbors.get('friendship')
            if len(friends) > agent.dunbar_number():
                for friend in self.rng.choice(friends,
                                              len(friends) - agent.dunbar_number(),
                                              replace=False):
                    friend.remove_friendship(agent)


    def remove_excess_professional_links(self) -> None:
        """
        Given a max number (30) this procedure cut the excess professional links.
        Is activated at every tick.
        :return: None
        """
        for agent in self.schedule.agents:
            friends = agent.get_neighbor_list('professional')
            if len(friends) > 30:
                for friend in self.rng.choice(friends, int(len(friends) - 30), replace=False):
                    friend.remove_professional(agent)


    def setup_oc_groups(self) -> None:
        """
        This procedure creates "criminal" type links within the families, based on the criminal
        tendency of the agents, in case the agents within the families are not enough, new members
        are taken outside.

        :return: None
        """
        # OC members are scaled down if we don't have 10K agents
        scaled_num_oc_families = np.ceil(
            self.num_oc_families * self.initial_agents / 10000 * self.num_oc_persons / 30)
        scaled_num_oc_persons = np.ceil(
            self.num_oc_persons * self.initial_agents / 10000)
        # families first.
        # we assume here that we'll never get a negative criminal tendency.
        oc_family_heads = extra.weighted_n_of(scaled_num_oc_families, self.schedule.agents, lambda x: x.criminal_tendency, self.rng)
        for head in oc_family_heads:
            head.oc_member = True
            candidates = [relative for relative in head.neighbors.get('household') if relative.age >= 18]
        if len(candidates) >= scaled_num_oc_persons - scaled_num_oc_families:  # family members will be enough
            members_in_families = extra.weighted_n_of(scaled_num_oc_persons - scaled_num_oc_families, candidates, lambda x: x.criminal_tendency, self.rng)
            # fill up the families as much as possible
            for member in members_in_families:
                member.oc_member = True
        else:  # take more as needed (note that this modifies the count of families)
            for candidate in candidates:
                candidate.oc_member = True
            out_of_family_candidates = [agent for agent in self.schedule.agents
                                        if not agent.oc_member]
            out_of_family_candidates = extra.weighted_n_of(
                scaled_num_oc_persons - len(candidates) - len(oc_family_heads),
                out_of_family_candidates, lambda x: x.criminal_tendency, self.rng)
            for out_of_family_candidate in out_of_family_candidates:
                out_of_family_candidate.oc_member = True
        # and now, the network with its weights..
        oc_members_pool = [oc_member for oc_member in self.schedule.agents
                           if oc_member.oc_member]
        for (i, j) in combinations(oc_members_pool, 2):
            i.add_criminal_link(j)


    def reset_oc_embeddedness(self) -> None:
        """
        Reset the Person.cached_oc_embeddedness of all agents, this procedure is activated every
        tick before committing crimes.
        :return: None
        """
        for agent in self.schedule.agents:
            agent.cached_oc_embeddedness = None

    def list_contains_problems(self, ego: Person, candidates:List[Person]) -> Union[bool, None]:
        """
        This procedure checks if there are any links between partners within the candidate pool.
        Returns True if there are, None if there are not. It is used during ProtonOc.setup_siblings
        procedure to avoid incestuous marriages.
        :param ego: Person, the agent
        :param candidates: Union[List[Person], Set[Person]], the candidates
        :return: Union[bool, None], True if there are links between partners, None otherwise.
        """
        all_potential_siblings = [ego] + ego.get_neighbor_list("sibling") + candidates + [sibling for candidate in
                                                                                          candidates for sibling in
                                                                                          candidate.neighbors.get(
                                                                                              'sibling')]
        for sibling in all_potential_siblings:
            if sibling.get_neighbor_list("partner") and sibling.get_neighbor_list("partner")[
                0] in all_potential_siblings:
                return True
   
    def setup_persons_and_friendship(self) -> None:
        """
        This procedure initializes the agents and creates the first "friendship" links based on an
        watts strogatz net.
        :return: None
        """
        watts_strogatz = nx.watts_strogatz_graph(self.initial_agents, 2, 0.1)
        for node in watts_strogatz.nodes():
            new_agent = Person(self)
            new_agent.init_person()
            self.schedule.add(new_agent)
            watts_strogatz.nodes[node].update({'person': new_agent})
        for node in list(watts_strogatz.nodes()):
            for neighbor in list(watts_strogatz.neighbors(node)):
                watts_strogatz.nodes[neighbor]['person'].make_friendship_link(
                    watts_strogatz.nodes[node]['person'])


    def setup_siblings(self) -> None:
        """
        Right now, during setup, links between agents are only those within households, between
        friends and related to the school. At this stage of the standard setup, agents are linked
        through "siblings" links outside the household. To simulate agents who have left the
        original household, agents who have children are taken and "sibling" links are created
        taking care not to create incestuous relationships.

        :return: None
        """
        agent_left_household = [p for p in self.schedule.agents if
                                p.neighbors.get('offspring')]
        # simulates people who left the original household.
        for agent in agent_left_household:
            num_siblings = self.rng.poisson(0.5)
            # 0.5 -> the number of links is N^3 agents, so let's keep this low at this stage links
            # with other persons are only relatives inside households and friends.
            candidates = [c for c in agent_left_household
                          if c not in agent.neighbors.get("household")
                          and abs(agent.age - c.age) < 5 and c != agent]
            # remove couples from candidates and their neighborhoods (siblings)
            if len(candidates) >= 50:
                candidates = self.rng.choice(candidates, 50, replace=False).tolist()
            while len(candidates) > 0 and self.list_contains_problems(agent, candidates):
                # trouble should exist, or check-all-siblings would fail
                potential_trouble = [x for x in candidates if agent.get_neighbor_list("partner")]
                trouble = self.rng.choice(potential_trouble)
                candidates.remove(trouble)
            targets = [agent] + self.rng.choice(candidates,
                                                min(len(candidates), num_siblings)).tolist()
            for sib in targets:
                if sib in agent_left_household:
                    agent_left_household.remove(sib)
            for target in targets:
                target.add_sibling_link(targets)
                # this is a good place to remind that the number of links in the sibling link
                # neighbors is not the "number of brothers and sisters"
                # because, for example, 4 brothers = 6 links.
            other_targets = targets + [s for c in targets for s in c.neighbors.get('sibling')]
            for target in other_targets:
                target.add_sibling_link(other_targets)


    def generate_households(self) -> None:
        """
        This procedure aggregates eligible agents into households based on the tables
        (ProtonOC.self.head_age_dist, ProtonOC.proportion_of_male_singles_by_age,
        ProtonOC.hh_type_dist, ProtonOC.partner_age_dist, ProtonOC.children_age_dist,
        ProtonOC.p_single_father) and mostly follows the third algorithm from Gargiulo et al. 2010
        (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0008828)

        :return: None
        """
        population = self.schedule.agents.copy()
        self.hh_size = self.household_sizes(self.initial_agents)
        complex_hh_sizes = list()
        # contain the sizes that fail to generate: we'll reuse those for complex households
        max_attempts_by_size = 50
        attempts_list = list()
        # We have two levels of iterating: the first level is the general attempts at generating
        # a household and the second level is the attempts at generating a household of a
        # particular size before giving up.
        for size in self.hh_size:
            success = False
            nb_attempts = 0
            while not success and nb_attempts < max_attempts_by_size:
                hh_members = list()
                nb_attempts += 1
                # pick the age of the head according to the size of the household
                head_age = extra.pick_from_pair_list(self.head_age_dist[size], self.rng)
                if size == 1:
                    male_wanted = (self.rng.random()
                                   < self.proportion_of_male_singles_by_age[head_age])
                    head = self.pick_from_population_pool_by_age_and_gender(head_age,
                                                                            male_wanted,
                                                                            population)
                    # Note that we don't "do" anything with the picked head: the fact that it gets
                    # removed from the population table when we pick it is sufficient for us.
                    if head:
                        success = True
                        attempts_list.append(nb_attempts)
                else:
                    # For household sizes greater than 1, pick a household type according to
                    # age of the head
                    hh_type = extra.pick_from_pair_list(self.hh_type_dist[head_age], self.rng)
                    if hh_type == "single_parent":
                        male_head = self.rng.random() \
                                    < float(self.p_single_father.columns.to_list()[0])
                    else:
                        male_head = True
                    if male_head:
                        mother_age = extra.pick_from_pair_list(self.partner_age_dist[head_age],
                                                               self.rng)
                    else:
                        mother_age = head_age
                    hh_members.append(self.pick_from_population_pool_by_age_and_gender(head_age,
                                                                                       male_head,
                                                                                       population))
                    if hh_type == "couple":
                        mother = self.pick_from_population_pool_by_age_and_gender(mother_age,
                                                                                  False,
                                                                                  population)
                        hh_members.append(mother)
                    num_children = size - len(hh_members)
                    for child in range(1, int(num_children) + 1):
                        if num_children in self.children_age_dist:
                            if mother_age in self.children_age_dist[num_children]:
                                child_age = extra.pick_from_pair_list(
                                    self.children_age_dist[num_children][mother_age], self.rng)
                                child = self.pick_from_population_pool_by_age(child_age,
                                                                              population)
                                hh_members.append(child)
                    hh_members = [memb for memb in hh_members if memb is not None]  # exclude Nones
                    if len(hh_members) == size:
                        # only generate the household if we got everyone we needed
                        success = True
                        attempts_list.append(nb_attempts)
                        family_wealth_level = hh_members[0].wealth_level
                        # if it's a couple, partner up the first two members and
                        # set the others as offspring
                        if hh_type == "couple":
                            hh_members[0].make_partner_link(hh_members[1])
                            couple = hh_members[0:2]
                            offsprings = hh_members[2:]
                            for partner in couple:
                                partner.make_parent_offsprings_link(offsprings)
                            for sibling in offsprings:
                                sibling.add_sibling_link(offsprings)
                        for member in hh_members:
                            member.make_household_link(hh_members)
                            member.wealth_level = family_wealth_level
                        self.families.append(hh_members)
                    else:
                        # in case of failure, we need to put the selected
                        # members back in the population
                        for member in hh_members:
                            population.append(member)
            if not success:
                complex_hh_sizes.append(size)
        if self.verbose:
            print("Complex size: " + str(len(complex_hh_sizes))
                  + str("/") + str(len(self.hh_size)))
        for comp_hh_size in complex_hh_sizes:
            comp_hh_size = int(min(comp_hh_size, len(population)))
            complex_hh_members = population[0:comp_hh_size]  # grab the first persons in the list
            max_age_index = [x.age
                             for x in complex_hh_members].index(max([x.age
                                                                     for x in complex_hh_members]))
            family_wealth_level = complex_hh_members[max_age_index].wealth_level
            for member in complex_hh_members:
                population.remove(member)  # remove persons from the population
                member.make_household_link(complex_hh_members)  # and link them up.
                member.wealth_level = family_wealth_level
            if len(complex_hh_members) > 1:
                self.families.append(complex_hh_members)
        if self.verbose:
            print("Singles " + str(len([x for x in self.hh_size if x == 1])))
            print("Families " + str(len(self.families)))
            print("Average of attempts " + str(np.mean(attempts_list)))


    def household_sizes(self, size: int) -> List[int]:
        """
        Loads a table with a probability distribution of household size and calculates household
        based on initial agents

        :param size: int, population size
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


    def pick_from_population_pool_by_age_and_gender(self,
                                                    age_wanted: int,
                                                    male_wanted: bool,
                                                    population: List[Person]) -> Union[Person,
                                                                                       None]:
        """
        Pick an agent with specific age and sex, None otherwise
        :param age_wanted: int, age wanted
        :param male_wanted: bool, gender wanted
        :param population: List[Person], the population
        :return: Union[Person, None], the agent or None
        """
        if not [x for x in population if x.gender_is_male == male_wanted and x.age == age_wanted]:
            return None
        picked_person = self.rng.choice(
            [x for x in population if x.gender_is_male == male_wanted and x.age == age_wanted])
        population.remove(picked_person)
        return picked_person


    def pick_from_population_pool_by_age(self, age_wanted: int,
                                         population: List[Person]) -> Union[Person, None]:
        """
        Pick an agent with specific age form population, None otherwise
        :param age_wanted: int, age wanted
        :param population: List[Person], the population
        :return: agent or None
        """
        if age_wanted not in [x.age for x in population]:
            return None
        picked_person = self.rng.choice([x for x in population if x.age == age_wanted])
        population.remove(picked_person)
        return picked_person


    def setup_education_levels(self) -> None:
        """
        Modify the self.education_levels attribute in-place. Given "n" levels of education
        (list_schools), for each level compute the correct amount of schools for each level,
        based on the number of agents.

        :return: None
        """
        list_schools = extra.df_to_lists(self.read_csv_city("schools"), split_row=False)
        for index, level in enumerate(list_schools):
            level[3] = np.ceil((level[3] / level[4]) * self.initial_agents)
            level.remove(level[4])
            self.education_levels[index + 1] = level


    def setup_schools(self) -> None:
        """
        Based on the number of agents and the attribute ProtonOC.education_levels,
        generate schools.
        :return: None
        """
        for level in self.education_levels.keys():
            for i_school in range(int(self.education_levels[level][3])):
                new_school = School(self, level)
                self.schools.append(new_school)


    def init_students(self) -> None:
        """
        Adds to schools the agents that meet the defined parameters of age and level of education
        and then creates connections between agents within the school.
        :return: None
        """
        for level in self.education_levels:
            row = self.education_levels[level]
            start_age = row[0]
            end_age = row[1]
            pool = [agent for agent in self.schedule.agents
                    if start_age <= agent.age <= end_age
                    and agent.education_level == level - 1
                    and agent.max_education_level >= level]
            for agent in pool:
                agent.enroll_to_school(level)
        for school in self.schools:
            conn = extra.decide_conn_number(school.my_students, 15)
            for student in school.my_students:
                total_pool = school.my_students.difference({student})
                conn_pool = list(self.rng.choice(list(total_pool), conn, replace=False))
                student.make_school_link(conn_pool)


    def setup(self, n_agent: int) -> None:
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
        for agent in [agent for agent in self.schedule.agents
                      if agent.my_job is None and agent.my_school is None and 18 <=
                      agent.age < self.retirement_age and agent.job_level > 1]:
            agent.find_job()
        self.init_professional_links()
        self.calculate_crime_multiplier()
        self.calculate_criminal_tendency()
        self.calculate_arrest_rate()
        self.setup_oc_groups()
        self.setup_facilitators()
        self.init_collector()
        self.datacollector.collect(self)
        for agent in self.schedule.agent_buffer(shuffled=True):
            agent.hobby = self.rng.integers(low=1, high=5, endpoint=True)
        self.calc_correction_for_non_facilitators()
        for agent in self.schedule.agents:
            if not agent.gender_is_male and agent.get_neighbor_list("offspring"):
                agent.number_of_children = len(agent.get_neighbor_list("offspring"))
        elapsed_time = time.time() - start
        hours = elapsed_time // 3600
        temp = elapsed_time - 3600 * hours
        minutes = temp // 60
        seconds = temp - 60 * minutes
        if self.verbose:
            print("Setup Completed in: " + "%d:%d:%d" % (hours, minutes, seconds))


    def assign_jobs_and_wealth(self) -> None:
        """
        This procedure modifies the job_level and wealth_level attributes of agents in-place.
        This is just a first assignment, and will be modified first by the multiplier then
        by adding neet status.

        :return: None
        """
        for agent in self.schedule.agent_buffer(shuffled=True):
            if agent.age > 16:
                agent.job_level = extra.pick_from_pair_list(
                    self.work_status_by_edu_lvl[agent.education_level][agent.gender_is_male],
                    self.rng)
                agent.wealth_level = extra.pick_from_pair_list(
                    self.wealth_quintile_by_work_status[agent.job_level][agent.gender_is_male],
                    self.rng)
            else:
                agent.job_level = 1
                agent.wealth_level = 1  # this will be updated by family membership


    def setup_inactive_status(self) -> None:
        """
        Based on ProtonOC.labour_status_by_age_and_sex table, this method modifies the job_level
        attribute of the agents in-place.

        :return: None
        """
        for agent in self.schedule.agent_buffer(shuffled=True):
            if 14 < agent.age < self.retirement_age \
                    and agent.job_level == 1 and self.rng.random() < \
                    self.labour_status_by_age_and_sex[agent.gender_is_male][agent.age]:
                agent.job_level = 0


    def setup_employers_jobs(self) -> None:
        """
        Given the ProtonOC.job_counts table this function generates the correct number of Jobs
        and Employers. Modify in-place Job.my_employer, Job.job_level and Employer.my_jobs.

        :return: None
        """
        # a small multiplier is added so to increase the pool to
        # allow for matching at the job level
        jobs_target = len([agent for agent in self.schedule.agents
                           if agent.job_level > 1 and agent.my_school is None
                           and 16 < agent.age < self.retirement_age]) * 1.2
        while len(self.jobs) < jobs_target:
            n = int(self.rng.choice(self.job_counts, 1))
            new_employer = Employer(self)
            self.employers.append(new_employer)
            for job in range(n):
                new_job = Job(self)
                self.jobs.append(new_job)
                new_job.my_employer = new_employer
                new_employer.my_jobs.append(new_job)
                new_job.job_level = self.random_level_by_size(n)


    def random_level_by_size(self, employer_size: Union[int, float]) -> int:
        """
        Given a float or int @employer_size this function returns the level to be assigned
        based on the table ProtonOC.jobs_by_company_size.
        :param employer_size: Union[int, float], the size
        :return: int, the level
        """
        most_similar_key = employer_size
        if employer_size not in self.jobs_by_company_size:
            min_dist = 1e10
            for key in self.jobs_by_company_size:
                if abs(employer_size - key) < min_dist:
                    most_similar_key = key
                    min_dist = abs(employer_size - key)
        return extra.pick_from_pair_list(self.jobs_by_company_size[most_similar_key], self.rng)


    def init_professional_links(self) -> None:
        """
        Creates connections between agents within the same Employer.
        :return: None
        """
        for employer in self.employers:
            employees = employer.employees()
            conn = extra.decide_conn_number(employees, 20)
            for employee in employees:
                total_pool = [agent for agent in employees if agent != employee]
                conn_pool = list(self.rng.choice(list(total_pool), conn, replace=False))
                employee.make_professional_link(conn_pool)


    def calculate_crime_multiplier(self) -> None:
        """
        Based on ProtonOC.c_range_by_age_and_sex this procedure modifies in-place
        the attribute ProtonOc.crime_multiplier
        :return: None
        """
        total_crime = 0
        for line in self.c_range_by_age_and_sex:
            people_in_cell = [agent for agent in self.schedule.agents if line[0][1] <
                              agent.age <= line[1][0] and agent.gender_is_male == line[0][0]]
            n_of_crimes = line[1][1] * len(people_in_cell)
            total_crime += n_of_crimes
        self.crime_multiplier = \
            self.number_crimes_yearly_per10k / 10000 * self.initial_agents / total_crime


    def calculate_criminal_tendency(self) -> None:
        """
        Based on the ProtonOC.c_range_by_age_and_sex distribution, this function calculates and
        assigns to each agent a value representing the criminal tendency. It modifies the attribute
        Person.criminal_tendency in-place.

        :return: None
        """
        for line in self.c_range_by_age_and_sex:
            # the line variable is composed as follows:
            # [[bool(gender_is_male), int(minimum age range)],
            # [int(maximum age range), float(c value)]]
            subpop = [agent for agent in self.schedule.agents if
                      line[0][1] <= agent.age <= line[1][0] and agent.gender_is_male == line[0][0]]
            if subpop:
                c = line[1][1]
                # c is the cell value. Now we calculate criminal-tendency with the factors.
                for agent in subpop:
                    agent.criminal_tendency = c
                    agent.update_criminal_tendency()
                # then derive the correction epsilon by solving
                # $\sum_{i} ( c f_i + \epsilon ) = \sum_i c$
                epsilon = c - np.mean([agent.criminal_tendency for agent in subpop])
                for agent in subpop:
                    agent.criminal_tendency += epsilon
        if self.intervention_is_on() and self.facilitator_repression:
            self.calc_correction_for_non_facilitators()


    def calc_correction_for_non_facilitators(self):
        """
        This function modifies the ProtonOC.correction_for_non_facilitators attribute of the model
        based on the number of agents and on the number of facilitators.
        :return: None
        """
        f = len([agent for agent in self.schedule.agents if agent.facilitator])
        n = len(self.schedule.agents)
        self.correction_for_non_facilitators = [
            (n - self.facilitator_repression_multiplier * f) / (n - f)] if f > 0 else 1.0


    def intervention_is_on(self) -> bool:
        """
        Returns True if there is an active intervention False otherwise.
        :return: bool, True if there is an active intervention False otherwise.
        """
        return self.ticks % self.ticks_between_intervention == 0 and self.intervention_start <= self.ticks < self.intervention_end


    def lognormal(self, mu: Union[float, int], sigma: Union[float, int]) -> float:
        """
        Draw samples from a log-normal distribution
        :param mu: float, mean
        :param sigma: float, standard deviation
        :return: float, sample
        """
        return np.exp(mu + sigma * self.rng.normal())


    def calculate_arrest_rate(self) -> None:
        """
        This gives the base probability of arrest, proportionally to the number of expected crimes
        in the first year. Modifies the attribute ProtonOC.arrest_rate in-place
        :return: None
        """
        self.arrest_rate = self.number_arrests_per_year / self.ticks_per_year / self.number_crimes_yearly_per10k / 10000 * self.initial_agents


    def assing_parents(self) -> None:
        """
        This function modifies in-place the Person.mother and Person.father attribute of agents,
        based on networks. This function is redundant, the information is already contained within
        the Person.neighbors attribute, it has been implemented to ensure faster access.
        :return: None
        """
        for agent in self.schedule.agents:
            if agent.neighbors.get("parent"):
                for parent in agent.neighbors.get("parent"):
                    if parent.gender_is_male:
                        agent.father = parent
                    else:
                        agent.mother = parent


    def choose_intervention_setting(self) -> None:
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


    def graduate_and_enter_jobmarket(self) -> None:
        """
        This enables students to move between levels of education and into the labor market.
        :return: None
        """
        primary_age = self.education_levels[1][0]
        for student in [agent for agent in self.schedule.agents
                        if agent.education_level == 0 and agent.age == primary_age
                        and agent.my_school is None]:
            student.enroll_to_school(1)
        for school in self.schools:
            end_age = self.education_levels[school.diploma_level][1]
            for student in [agent for agent in school.my_students if agent.age == end_age + 1]:
                student.leave_school()
                student.education_level = school.diploma_level
                if school.diploma_level + 1 in self.education_levels.keys() \
                        and school.diploma_level + 1 <= student.max_education_level:
                    student.enroll_to_school(school.diploma_level + 1)
                else:
                    student.job_level = extra.pick_from_pair_list(
                        self.work_status_by_edu_lvl[student.education_level][student.gender_is_male],
                        self.rng)
                    student.wealth_level = extra.pick_from_pair_list(
                        self.wealth_quintile_by_work_status[student.job_level][student.gender_is_male],
                        self.rng)
                    if 14 < student.age < self.retirement_age and student.job_level == 1 \
                            and self.rng.random() < \
                            self.labour_status_by_age_and_sex[student.gender_is_male][student.age]:
                        student.job_level = 0


    def let_migrants_in(self) -> None:
        """
        if ProtonOC.migration_on is equal to True this procedure inserts foreign agents within the
        population based on available jobs. These new agents are instantiated and they are given
        a job

        :return: None
        """
        if self.migration_on:
            # calculate the difference between deaths and birth
            to_replace = self.initial_agents - len(self.schedule.agents) \
                if self.initial_agents - len(self.schedule.agents) > 0 else 0
            free_jobs = [job for job in self.jobs if job.my_worker]
            n_to_add = np.min([to_replace, len(free_jobs)])
            self.number_migrants += n_to_add
            for job in self.rng.choice(free_jobs, n_to_add, replace=False):
                # we do not care about education level and wealth of migrants, as those variables
                # exist only in order to generate the job position.
                new_agent = Person(self)
                new_agent.init_person()
                self.schedule.add(new_agent)
                new_agent.my_job = job
                job.my_worker = new_agent
                total_pool = [candidate for candidate in new_agent.my_job.my_employer.employees()
                              if candidate != new_agent]
                employees = list(
                    self.rng.choice(total_pool, extra.decide_conn_number(total_pool, 20,
                                                                         also_me=False),
                                    replace=False))
                new_agent.make_professional_link(employees)
                new_agent.bird_tick = self.ticks - (self.rng.integers(0, 20) + 18) * self.ticks_per_year
                new_agent.wealth_level = job.job_level
                new_agent.migrant = True


    def commit_crimes(self) -> None:
        """
        This procedure is central in the model, allowing agents to find accomplices and commit
        crimes. Based on the table ProtonOC.c_range_by_age_and_sex, the number of crimes and the
        subset of the agents who commit them is selected. For each crime a single agent is selected
        and if necessary activates the procedure that allows the agent to find accomplices.
        Criminal groups are append within the list co_offender_groups.

        :return: None
        """
        co_offender_groups = list()
        co_offender_started_by_oc = list()
        for cell, value in self.c_range_by_age_and_sex:
            people_in_cell = [agent for agent in self.schedule.agents if
                              cell[1] <= agent.age <= value[0]
                              and agent.gender_is_male == cell[0]]
            target_n_of_crimes = \
                value[1] * len(people_in_cell) / self.ticks_per_year * self.crime_multiplier
            for _target in np.arange(np.round(target_n_of_crimes)):
                self.number_crimes += 1
                agent = extra.weighted_one_of(people_in_cell, lambda x: x.criminal_tendency, self.rng)
                number_of_accomplices = self.number_of_accomplices()
                accomplices = agent.find_accomplices(number_of_accomplices)
                # this takes care of facilitators as well.
                co_offender_groups.append(accomplices)
                if agent.oc_member:
                    co_offender_started_by_oc.append(accomplices)
                # check for big crimes started from a normal guy
                if len(accomplices) > self.this_is_a_big_crime \
                        and agent.criminal_tendency < self.good_guy_threshold:
                    self.big_crime_from_small_fish += 1
        for co_offender_group in co_offender_groups:
            extra.commit_crime(co_offender_group)
        for co_offenders_by_OC in co_offender_started_by_oc:
            for agent in [agent for agent in co_offenders_by_OC if not agent.oc_member]:
                agent.new_recruit = self.ticks
                agent.oc_member = True
                if agent.father:
                    if agent.father.oc_member:
                        self.number_offspring_recruited_this_tick += 1
                if agent.target_of_intervention:
                    self.number_protected_recruited_this_tick += 1
        criminals = list(chain.from_iterable(co_offender_groups))
        if criminals:
            if self.intervention_is_on() and self.facilitator_repression:
                for criminal in criminals:
                    criminal.arrest_weight = self.facilitator_repression_multiplier \
                        if criminal.facilitator else 1
            else:
                if self.intervention_is_on() and self.oc_boss_repression and len(
                        [agent for agent in criminals if agent.oc_member]) >= 1:
                    for criminal in criminals:
                        if not criminal.oc_member:
                            criminal.arrest_weight = 1
                    extra.calculate_oc_status([agent for agent in criminals if agent.oc_member])
                else:
                    # no intervention active
                    for criminal in criminals:
                        criminal.arrest_weight = 1
            arrest_mod = self.number_arrests_per_year / self.ticks_per_year / 10000 * len(self.schedule.agents)
            target_n_of_arrest = np.floor(
                arrest_mod + 1
                if self.rng.random() < (arrest_mod - np.floor(arrest_mod))
                else 0)
            for agent in extra.weighted_n_of(target_n_of_arrest, criminals,
                                             lambda x: x.arrest_weight, self.rng):
                agent.get_caught()


    def number_of_accomplices(self) -> int:
        """
        Pick a group size from ProtonOC.num_co_offenders_dist distribution and substract one to get
        the number of accomplices
        :return: int
        """
        return extra.pick_from_pair_list(self.num_co_offenders_dist, self.rng) - 1

    def update_meta_links(self, agents: Set[Person]) -> None:
        """
        This method creates a new temporary graph that is used to colculate the
        oc_embeddedness of an agent.

        :param agents: Set[Person], the agentset
        :return: None
        """
        self.meta_graph = nx.Graph()
        for agent in agents:
            self.meta_graph.add_node(agent.unique_id)
            for in_radius_agent in agent.agents_in_radius(
                    1):  # limit the context to the agents in the radius of interest
                self.meta_graph.add_node(in_radius_agent.unique_id)
                w = 0
                for net in Person.network_names:
                    if in_radius_agent in agent.neighbors.get(net):
                        if net == "criminal":
                            if in_radius_agent in agent.num_co_offenses:
                                w += agent.num_co_offenses[in_radius_agent]
                        else:
                            w += 1
                self.meta_graph.add_edge(agent.unique_id, in_radius_agent.unique_id, weight=1 / w)

    def retire_persons(self) -> None:
        """
        Agents that reach the self.retirement_age are retired.
        :return: None
        """
        to_retire = [agent for agent in self.schedule.agents
                     if agent.age >= self.retirement_age and not agent.retired]
        for agent in to_retire:
            agent.retired = True
            if agent.my_job is not None:
                agent.my_job.my_worker = None
                agent.my_job = None
                agent.neighbors.get("professional").clear()
                # Figure out how to preserve socio-economic status (see issue #22)

    def make_baby(self) -> None:
        """
        Based on the ProtonOC.fertility_table this procedure create new agents taking into account
        the possibility that the model is set to ProtonOC.constant_population.
        :return: None
        """
        if self.constant_population:
            breeding_target = self.initial_agents - len(self.schedule.agents)
            if breeding_target > 0:
                breeding_pool = self.rng.choice([agent for agent in self.schedule.agents if
                                                14 <= agent.age <= 50
                                                 and not agent.gender_is_male],
                                                size=breeding_target * 10, replace=False)
                for agent in extra.weighted_n_of(breeding_target, breeding_pool,
                                                 lambda x: x.p_fertility(), self.rng):
                    agent.init_baby()
        else:
            for agent in [agent for agent in self.schedule.agents if
                          14 <= agent.age <= 50 and not agent.gender_is_male]:
                if self.rng.random() < agent.p_fertility():
                    agent.init_baby()

    def make_people_die(self) -> None:
        """
        Based on ProtonOC.p_mortality table agents die.
        :return: None
        """
        dead_agents = list()
        for agent in self.schedule.agent_buffer(True):
            if self.rng.random() < agent.p_mortality() or agent.age > 119:
                dead_agents.append(agent)
                if self.removed_fatherships:
                    for removed in self.removed_fatherships:
                        if agent == removed[1] or agent == removed[2]:
                            self.removed_fatherships.remove(removed)
                if agent.facilitator:
                    new_facilitator = self.rng.choice([agent for agent in self.schedule.agents
                                                       if not agent.facilitator
                                                       and not agent.oc_member and agent.age > 18])
                    new_facilitator.facilitator = True
                self.number_deceased += 1
                if agent.my_job is not None:
                    agent.my_job.my_worker = None
                if agent.my_school is not None:
                    agent.my_school.my_students.remove(agent)
                agent.die()
        for agent in dead_agents:
            self.schedule.remove(agent)
            del agent


if __name__ == "__main__":
    model = ProtonOC()
    model.intervention = "baseline"
    model.run(1000, 60, verbose=True)
