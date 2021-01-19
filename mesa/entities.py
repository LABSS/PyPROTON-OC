from __future__ import annotations
from typing import List, Set, Union, Dict
import typing
if typing.TYPE_CHECKING:
    from model import ProtonOC
from mesa import Agent
import numpy as np
import networkx as nx
from itertools import chain
import extra


class Person(Agent):

    max_id: int = 0
    network_names: List[str] = [
        'sibling',
        'offspring',
        'parent',
        'partner',
        'household',
        'friendship',
        'criminal',
        'professional',
        'school']

    def __init__(self, model: ProtonOC):
        self.unique_id: int = Person.max_id
        Person.max_id += 1
        super().__init__(self.unique_id, model=model)
        self.model = model
        # networks
        self.neighbors: Dict = self.networks_init()

        self.gender_is_male: bool = self.model.rng.choice([True, False])  # True male False female
        self.prisoner: bool = False
        self.age: Union[int, float] = 0
        self.sentence_countdown: Union[int, float] = 0
        self.num_crimes_committed: Union[int, float] = 0
        self.num_crimes_committed_this_tick: Union[int, float] = 0
        self.education_level: Union[int, float] = 0  # level: last school I finished (for example, 4: I finished university)
        self.max_education_level: Union[int, float] = 0
        self.wealth_level: Union[int, float] = 1
        self.job_level: Union[int, float] = 0
        self.my_job: Union[Job, None] = None  # could be known from `one_of job_link_neighbors`, but is stored directly for performance _ need to be kept in sync
        self.birth_tick: Union[int, float] = self.model.ticks
        self.father: Union[Person, None] = None
        self.mother: Union[Person, None] = None
        self.propensity: Union[int, float] = self.model.lognormal(self.model.nat_propensity_m, self.model.nat_propensity_sigma)
        self.oc_member: bool = False
        self.cached_oc_embeddedness: Union[int, float, None] = None
        self.retired: bool = False
        self.number_of_children: Union[int, float] = 0
        self.facilitator: bool = False
        self.hobby: int = self.model.rng.integers(low=1, high=5, endpoint=True)
        self.new_recruit: int = -2
        self.migrant: bool = False
        self.criminal_tendency: float = 0
        self.my_school: Union[None, School] = None
        self.target_of_intervention: bool = False
        self.arrest_weight: Union[int, float] = 0
        self.num_co_offenses: Dict = dict()  # criminal-links
        self.co_off_flag: Dict = dict()  # criminal-links


    def __repr__(self):
        return "Agent: " + str(self.unique_id)


    def calculate_age(self) -> None:
        """
        This method modifies the Person.age attribute in-place. Calculates the age of the agent
        base on Person.birth_tick and Person.model.ticks.
        :return: None
        """
        self.age = extra._age(self.model.ticks, self.birth_tick)


    def networks_init(self) -> Dict:
        """
        This method generates the structure of the agent's networks that will be preserved
        within the Person.neighbors attribute.
        :return: Dict
        """
        return {i: set() for i in Person.network_names}


    def neighbors_range(self, netname: str, dist: int):
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

    def makePartnerLinks(self, asker):
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
        self.num_co_offenses[asker] = 1
        asker.neighbors.get("criminal").add(self)
        asker.num_co_offenses[self] = 1

    def remove_link(self, forlorn, kind):
        self.neighbors.get(kind).discard(forlorn)
        forlorn.neighbors.get(kind).discard(self)

    def remove_friendship(self, forlorn):
        self.remove_link(forlorn, 'friendship')

    def remove_professional(self, forlorn):
        self.remove_link(forlorn, 'professional')

    def age_between(self, low, high):
        return self.age >= low and self.age < high

    def potential_friends(self):
        """
        The potential friends in my networks
        :return: set, potential friends
        """
        return set(self.family_link_neighbors()).union(self.neighbors.get("school")).union(self.neighbors.get("professional")).difference(
            self.neighbors.get("friendship"))

    def dunbar_number(self):
        return (150 - abs(self.age - 30))

    def init_person(self):  # person command
        """
        This method modifies the attributes of the person instance based on the model's
        stats_tables as part of the initial setup of the model agents.
        """
        row = extra.weighted_one_of(self.model.age_gender_dist, lambda x: x[-1],
                                    self.model.rng)  # select a row from our age_gender distribution
        self.birth_tick = 0 - row[0] * self.model.ticks_per_year  # ...and set age... =
        self.calculate_age()
        self.gender_is_male = bool(row[1])  # ...and gender according to values in that row.
        self.retired = self.age >= self.model.retirement_age  # persons older than retirement_age are retired
        # education level is chosen, job and wealth follow in a conditioned sequence
        self.max_education_level = extra.pick_from_pair_list(self.model.edu[self.gender_is_male], self.model.rng)
        # apply model-wide education modifier
        if self.model.education_modifier != 1.0:
            if self.model.rng.random() < abs(self.model.education_modifier - 1):
                self.max_education_level = self.max_education_level + (1 if (self.model.education_modifier > 1) else -1)
                self.max_education_level = len(self.model.edu[True]) if self.max_education_level > len(
                    self.model.edu[True]) else 1 if self.max_education_level < 1 else self.max_education_level
        # limit education by age
        # notice how this deforms a little the initial setup
        self.education_level = self.max_education_level
        for level in sorted(list(self.model.education_levels.keys()), reverse=True):
            max_age = self.model.education_levels[level][1]
            if self.age <= max_age or self.education_level > self.max_education_level:
                self.education_level = level - 1
        self.propensity = self.model.lognormal(self.model.nat_propensity_m, self.model.nat_propensity_sigma)

    def enroll_to_school(self, level):
        """
        Given a level of education, this method chooses a school where to enroll the agent
        and modifies my_school atribute in-place.
        :param level: int, level of education to enroll
        """
        potential_school = list()
        for school in [agent.my_school for agent in self.neighbors.get("household") if agent.my_school]:
            if school.diploma_level == level:
                potential_school.append(school)
        if potential_school:
            self.my_school = self.model.rng.choice(potential_school)
        else:
            potential_school = [x for x in self.model.schools if x.diploma_level == level]
            self.my_school = self.model.rng.choice(potential_school)
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
        self.criminal_tendency *= 4.50 if self.oc_member else 1.0

    def family_link_neighbors(self):
        """
        This function returns a list of all agents that have sibling,offspring,partner type connection with the agent.
        :return: list, the agents
        """
        return self.get_link_list("sibling") + self.get_link_list("offspring") + self.get_link_list("partner")

    def remove_from_household(self):
        """
        This method removes the agent from household, keeping the networks consistent.
        Modify the Person.neighbors attribute in-place
        :return: None
        """
        for member in self.neighbors.get("household").copy():
            if self in member.neighbors.get("household"):
                member.neighbors.get("household").remove(self)
                self.neighbors.get("household").remove(member)

    def leave_school(self):
        """
        This method modifies in-place the my_school attribute and the School.my_students attribute.
        :return: None
        """
        self.my_school.my_students.remove(self)
        self.my_school = None

    def just_changed_age(self):
        """
        If the agent has changed years during this tick this function returns true, otherwise it returns false.
        :return: bool,
        """
        return np.floor((self.model.ticks - self.birth_tick) / self.model.ticks_per_year) \
               == ((self.model.ticks - self.birth_tick) / self.model.ticks_per_year)

    def update_unemployment_status(self):
        """
        This function modifies the job_level attribute in-place according to table model.labour_status_by_age_and_sex
        :return: None
        """
        self.job_level = 0 if self.model.rng.random() < self.model.labour_status_by_age_and_sex[self.gender_is_male][
            self.age] else 1

    def find_accomplices(self, n_of_accomplices):
        """
        This method is used to find accomplices during commit_crimes procedure
        :param n_of_accomplices: int, number of accomplices
        :return: list, of Person objects
        """
        if n_of_accomplices == 0:
            return [self]
        else:
            d = 1  # start with a network distance of 1
            accomplices = set()
            facilitator_needed = n_of_accomplices >= self.model.threshold_use_facilitators and not self.facilitator
            if facilitator_needed:
                n_of_accomplices -= 1  # save a slot for the facilitator
            while len(accomplices) < n_of_accomplices and d <= self.model.max_accomplice_radius:
                # first create the group
                candidates = sorted(self.agents_in_radius(d), key=lambda x: self.candidates_weight(x))
                while len(accomplices) < n_of_accomplices and len(candidates) > 0:
                    candidate = candidates[0]
                    candidates.remove(candidate)
                    accomplices.add(candidate)
                    if candidate.facilitator:
                        n_of_accomplices += 1
                        facilitator_needed = False
                d += 1
            if facilitator_needed:
                # Search a facilitator into my networks
                available_facilitators = [facilitator for facilitator in set(chain.from_iterable(
                    [agent.agents_in_radius(self.model.max_accomplice_radius) for agent in accomplices])) if
                                          facilitator.facilitator]
                if available_facilitators:
                    accomplices.add(self.model.rng.choice(available_facilitators))
            if len(accomplices) < n_of_accomplices:
                self.model.crime_size_fails += 1
            accomplices.add(self)
            if n_of_accomplices >= self.model.threshold_use_facilitators:
                if [agent for agent in accomplices if agent.facilitator]:
                    self.model.facilitator_crimes += 1
                else:
                    self.model.facilitator_fails += 1
        return list(accomplices)

    def candidates_weight(self, agent):
        """
        This is what in the paper is called r - this is r R is then operationalised as the proportion
        of OC members among the social relations of each individual (comprising family, friendship, school,
        working and co-offending relations)
        :return: float, the candidates weight
        """
        return -1 * (extra.social_proximity(self,
                                            agent) * self.oc_embeddedness() * self.criminal_tendency) if agent.oc_member \
            else (extra.social_proximity(self, agent) * self.criminal_tendency)

    def _agents_in_radius(self, context=network_names):
        """
        It finds the agents distant 1 in the specified networks, by default it finds it on all networks.
        :param context: list, of strings, limit to networks name
        :return: set, of Person objects
        """
        agents_in_radius = set()
        for net in context:
            if self.neighbors.get(net):
                for agent in self.neighbors.get(net):
                    agents_in_radius.add(agent)
        return agents_in_radius

    def agents_in_radius(self, d, context=network_names):
        """
        It finds the agents distant "d" in the specified networks "context", by default it finds it on all networks.
        :param d: int, the distance
        :param context: list, of strings, limit to networks name
        :return: set, of Person objects
        """
        # todo: This function must be speeded up, radius(3) on all agents with 1000 initial agents, t = 1.05 sec
        radius = self._agents_in_radius(context)
        if d == 1:
            return radius
        else:
            for di in range(d - 1):
                for agent_in_radius in radius:
                    radius = radius.union(agent_in_radius._agents_in_radius(context))
            if self in radius:
                radius.remove(self)
            return radius

    def oc_embeddedness(self):
        """
        Calculates the cached_oc_embeddedness of self.
        :return: float, the cached_oc_embeddedness
        """
        if self.cached_oc_embeddedness is None:
            # only calculate oc-embeddedness if we don't have a cached value
            self.cached_oc_embeddedness = 0
            # start with an hypothesis of 0
            agents = self.agents_in_radius(self.model.oc_embeddedness_radius)
            oc_members = [agent for agent in agents if agent.oc_member]
            # this needs to include the caller
            agents.add(self)
            if oc_members:
                self.model.update_meta_links(agents)
                self.cached_oc_embeddedness = self.find_oc_weight_distance(oc_members) / self.find_oc_weight_distance(
                    agents)
        return self.cached_oc_embeddedness

    def find_oc_weight_distance(self, agents):
        """
        Based on the graph self.model.meta_graph calculates the weighted distance of self from each agent passed to the agents parameter
        :param agents: list or set, of Person objects
        :return: float, the distance
        """
        if self in agents:
            agents.remove(self)
        distance = 0
        for agent in agents:
            distance += 1 / nx.algorithms.shortest_paths.weighted.dijkstra_path_length(self.model.meta_graph,
                                                                                       self.unique_id, agent.unique_id,
                                                                                       weight='weight')
        return distance

    def find_oc_distance(self, agents):
        """
        Based on the graph self.model.meta_graph calculates the weighted distance of self from each agent passed to the agents parameter
        :param agents: list or set, of Person objects
        :return: float, the distance
        """
        if self in agents:
            agents.remove(self)
        distance = 0
        for agent in agents:
                distance += self.model.meta_graph[self.unique_id][agent.unique_id]["weight"]
        return distance




    def calculate_oc_member_position(self):
        """
        Calculate the oc-member position of self
        :return: float, the oc-member-position
        """
        n = len([agent for agent in self.agents_in_radius(1) if agent.oc_member])
        my_oc_crim = [agent for agent in self.neighbors.get("criminal") if agent.oc_member]
        return n + np.sum([self.num_co_offenses[agent] for agent in my_oc_crim]) - len(my_oc_crim)

    def get_caught(self):
        """
        When an agent is caught during a crime and goes to prison, this procedure is activated.
        :return: None
        """
        self.model.number_law_interventions_this_tick += 1
        self.model.people_jailed += 1
        self.prisoner = True
        if self.gender_is_male:
            self.sentence_countdown = extra.pick_from_pair_list(self.model.male_punishment_length, self.model.rng)
        else:
            self.sentence_countdown = extra.pick_from_pair_list(self.model.female_punishment_length, self.model.rng)
        self.sentence_countdown = self.sentence_countdown * self.model.punishment_length
        if self.my_job:
            self.my_job.my_worker = None
            self.my_job = None
            self.job_level = 1
        if self.my_school:
            self.leave_school()
        self.neighbors.get("professional").clear()
        self.neighbors.get("school").clear()
        # we keep the friendship links and the family links

    def p_fertility(self):
        """
        Calculate the fertility
        :return: flot, the fertility
        """
        if np.min([self.number_of_children, 2]) in self.model.fertility_table[self.age]:
            return self.model.fertility_table[self.age][np.min([self.number_of_children, 2])] / self.model.ticks_per_year
        else:
            return 0

    def p_mortality(self):
        """
        Base on the table self.model.mortality_table calculate a probability that this agent die
        :return:
        """
        if self.age in self.model.mortality_table:
            p = self.model.mortality_table[self.age][self.gender_is_male] / self.model.ticks_per_year
        else:
            # if there's no key, we remove the agent
            p = 1
        return p

    def init_baby(self):
        """
        This method is for mothers only and allows to create new agents
        :return: None
        """
        self.number_of_children += 1
        self.model.number_born += 1
        new_agent = Person(self.model)
        self.model.schedule.add(new_agent)
        new_agent.wealth_level = self.wealth_level
        new_agent.birth_tick = self.model.ticks
        new_agent.mother = self
        if self.get_link_list("offspring"):
            new_agent.addSiblingLinks(self.get_link_list("offspring"))
        self.makeParent_OffspringsLinks(new_agent)
        if self.get_link_list("partner"):
            dad = self.get_link_list("partner")[0]
            dad.makeParent_OffspringsLinks(new_agent)
            new_agent.father = dad
            new_agent.max_education_level = dad.max_education_level
        else:
            new_agent.max_education_level = self.max_education_level
        new_agent.makeHouseholdLinks(self.get_link_list("household"))

    def die(self):
        """
        When an agent dies all his links cease to exist.
        :return: None
        """
        neighbors = self.agents_in_radius(1)
        for agent in neighbors:
            for net in self.network_names:
                if self in agent.neighbors.get(net):
                    agent.neighbors.get(net).remove(self)


class Job():
    max_id = 0
    def __init__(self, m):
        self.m = m
        self.job_level = 0
        self.my_employer = 0
        self.my_worker = None
        self.unique_id = Job.max_id
        Job.max_id = Job.max_id + 1

    def __repr__(self):
        return "Job: " + str(self.unique_id) + " Level: " + str(self.job_level)


class Employer():
    max_id = 0
    def __init__(self, model: ProtonOC):
        self.my_jobs = list()
        self.model = model
        self.unique_id = Employer.max_id
        Employer.max_id = Employer.max_id + 1

    def __repr__(self):
        return "Employer: " + str(self.unique_id)

    def create_job(self, level: int, worker):
        newjob = Job(self.model)
        newjob.level = level
        worker.my_job = newjob
        self.my_jobs.append(newjob)

    def employees(self):
        return [x.my_worker for x in self.my_jobs if x.my_worker != None]


class School():
    max_id = 0
    def __init__(self, model: ProtonOC, diploma_level: int):
        self.model = model
        self.diploma_level = diploma_level
        self.my_students = set()
        self.unique_id = School.max_id
        School.max_id = School.max_id + 1

    def __repr__(self):
        return "School: " + str(self.unique_id) + " Level: " + str(self.diploma_level)


if __name__ == "__main__":
    pass
