# MIT License
#
# Copyright (c) 2019 LABSS(Francesco Mattioli, Mario Paolucci)
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
from typing import List, Set, Union, Dict
import typing
if typing.TYPE_CHECKING:
    from .model import ProtonOC
from mesa import Agent
import networkx as nx
from itertools import chain
import extra
import numpy as np


class Person(Agent):

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
        self.unique_id: int = model.max_ids["person"]
        model.max_ids["person"] += 1
        super().__init__(self.unique_id, model=model)
        self.model = model
        # networks
        self.neighbors: Dict = self.networks_init()  #todo: this could be a Subclassed-dict
        self.gender_is_male: bool = self.model.random.choice([True, False])  # True male False female
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
        self.birth_tick: Union[int, float] = self.model.tick
        self.father: Union[Person, None] = None
        self.mother: Union[Person, None] = None
        self.propensity: Union[int, float] = self.model.lognormal(self.model.nat_propensity_m, self.model.nat_propensity_sigma)
        self.oc_member: bool = False
        self.cached_oc_embeddedness: Union[int, float, None] = None
        self.retired: bool = False
        self.number_of_children: Union[int, float] = 0
        self.facilitator: bool = False
        self.hobby: int = self.model.random.integers(low=1, high=5, endpoint=True)
        self.new_recruit: int = -2
        self.migrant: bool = False
        self.criminal_tendency: float = 0
        self.my_school: Union[None, School] = None
        self.target_of_intervention: bool = False
        self.arrest_weight: Union[int, float] = 0
        self.num_co_offenses: Dict = dict()  # criminal-links


    def __repr__(self):
        return "Agent: " + str(self.unique_id)

    def __hash__(self):
        return self.unique_id


    def calculate_age(self) -> None:
        """
        This method modifies the Person.age attribute in-place. Calculates the age of the agent
        base on Person.birth_tick and Person.model.ticks.
        :return: None
        """
        self.age = extra._age(self.model.tick, self.birth_tick)


    def networks_init(self) -> Dict:
        """
        This method generates the structure of the agent's networks that will be preserved
        within the Person.neighbors attribute.
        :return: Dict
        """
        return {i: set() for i in Person.network_names}


    def neighbors_range(self, netname: str, dist: int) -> Set[Person]:
        """
        Given the name of a network @netname returns the agents in radius @dist from this agent.
        :param netname: str: the network name
        :param dist: int, the distance
        :return: Set[Person], a set of agents
        """
        return extra.find_neighb(netname, dist, set(), {self}) - {self}


    def isneighbor(self, other: Person) -> bool:
        """
        Given another agent @other this function returns true if the two agents are neighbors, false otherwise.
        :param other: Person, the other agent
        :return: bool, true if the two agents are neighbors, false otherwise.
        """
        return any([other in self.neighbors[x] for x in Person.network_names])

    def step(self):
        pass


    def make_friendship_link(self, asker: Person) -> None:
        """
        Create a two-way friend links in-place
        :param asker: agent
        :return: None
        """
        self.neighbors.get("friendship").add(asker)
        asker.neighbors.get("friendship").add(self)

    def make_professional_link(self, asker: Union[Person, List[Person]]) -> None:
        """
        Create a two-way professional links in-place
        :param asker: Union[Person, List[Person]]
        :return: None
        """
        if type(asker) == list:
            for person in asker:
                self.neighbors.get("professional").add(person)
                person.neighbors.get("professional").add(self)
        else:
            self.neighbors.get("professional").add(asker)
            asker.neighbors.get("professional").add(self)

    def add_sibling_link(self, targets: List[Person]) -> None:
        """
        Create a two-way sibling links in-place
        :param targets: List[Person]
        :return: None
        """
        for x in targets:
            if x != self:
                self.neighbors.get("sibling").add(x)
                x.neighbors.get("sibling").add(self)

    def make_household_link(self, targets: List[Person]) -> None:
        """
        Create a two-way household link in-place
        :param targets: List[Person]
        :return: None
        """
        for x in targets:
            if x != self:
                self.neighbors.get("household").add(x)
                x.neighbors.get("household").add(self)

    def make_partner_link(self, asker: Person) -> None:
        """
        Create a two-way partner link in-place
        :param asker: Person
        :return: None
        """
        self.neighbors.get("partner").add(asker)
        asker.neighbors.get("partner").add(self)

    def make_parent_offsprings_link(self, asker: Union[List[Person], Person]) -> None:
        """
        Create a link between parent and offspring. Askers are the offspring.
        :param asker: Union[List[Person], Person]
        :return: None
        """
        if type(asker) == list:
            for person in asker:
                self.neighbors.get("offspring").add(person)
                person.neighbors.get("parent").add(self)
        else:
            self.neighbors.get("offspring").add(asker)
            asker.neighbors.get("parent").add(self)

    def make_school_link(self, asker: Union[List[Person], Person]) -> None:
        """
        Create a two-way school link in-place
        :param asker: Union[List[Person], Person]
        :return: None
        """
        if type(asker) == list:
            for person in asker:
                self.neighbors.get("school").add(person)
                person.neighbors.get("school").add(self)
        else:
            self.neighbors.get("school").add(asker)
            asker.neighbors.get("school").add(self)

    def add_criminal_link(self, asker: Person) -> None:
        """
        Create a two-way criminal links in-place and update the connection weight
        :param asker: Person
        :return: None
        """
        self.neighbors.get("criminal").add(asker)
        self.num_co_offenses[asker] = 0
        asker.neighbors.get("criminal").add(self)
        asker.num_co_offenses[self] = 0

    def remove_link(self, forlorn: Person, context: str) -> None:
        """
        Removes a @context type link between @self and @forlorn :(
        :param forlorn: Person
        :param context: str, the network name
        :return: None
        """
        if self not in forlorn.neighbors.get(context):
            raise Exception(str(forlorn) + str(" not in context: " + context + " of " + str(self)))
        else:
            self.neighbors.get(context).discard(forlorn)
            forlorn.neighbors.get(context).discard(self)

    def remove_friendship(self, forlorn):
        self.remove_link(forlorn, 'friendship')

    def remove_professional(self, forlorn):
        self.remove_link(forlorn, 'professional')


    def potential_friends(self) -> Set[Person]:
        """
        This function searches for potential friends within school and professional networks.
        :return: set, potential friends
        """
        return set(self.family_link_neighbors()).union(
            self.neighbors.get("school")).union(
            self.neighbors.get("professional")).difference(
            self.neighbors.get("friendship"))

    def dunbar_number(self) -> int:
        """
        Calculate Dunbar number, https://en.wikipedia.org/wiki/Dunbar%27s_number
        :return: int, Dunbar number
        """
        return 150 - abs(self.age - 30)

    def init_person(self) -> None:
        """
        This method modifies the attributes of the person instance based on the model's
        stats_tables as part of the initial setup of the model agents.
        :return: None
        """
        row = extra.weighted_one_of(self.model.age_gender_dist, lambda x: x[-1],
                                    self.model.random)  # select a row from our age_gender distribution
        self.birth_tick = 0 - row[0] * self.model.ticks_per_year  # ...and set age... =
        self.calculate_age()
        self.gender_is_male = bool(row[1])  # ...and gender according to values in that row.
        self.retired = self.age >= self.model.retirement_age  # persons older than retirement_age are retired
        # education level is chosen, job and wealth follow in a conditioned sequence
        self.max_education_level = extra.pick_from_pair_list(self.model.edu[self.gender_is_male], self.model.random)
        # apply model-wide education modifier
        if self.model.education_modifier != 1.0:
            if self.model.random.random() < abs(self.model.education_modifier - 1):
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

    def enroll_to_school(self, level: int) -> None:
        """
        Given a level of education, this method chooses a school where to enroll the agent
        and modifies my_school atribute in-place.
        :param level: int, level of education to enroll
        """
        potential_school = list()
        for school in [agent.my_school for agent in self.neighbors.get("household") if
                       agent.my_school]:
            if school.diploma_level == level:
                potential_school.append(school)
        if potential_school:
            self.my_school = self.model.random.choice(potential_school)
        else:
            potential_school = [x for x in self.model.schools if x.diploma_level == level]
            self.my_school = self.model.random.choice(potential_school)
        self.my_school.my_students.add(self)

    def get_neighbor_list(self, net_name: str) -> Union[List[Person], List]:
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

    def find_job(self) -> None:
        """
        This method assigns a job to the Person based on those available and their level. Modify in-place the
        my_worker attribute of Job and the my_job attribute of Person.
        :return: None
        """
        jobs_pool = [j for j in self.model.jobs if j.my_worker is None and j.job_level == self.job_level]
        if not jobs_pool:
            jobs_pool = [j for j in self.model.jobs if j.my_worker is None and j.job_level < self.job_level]
        if jobs_pool:
            the_job = self.model.random.choice(jobs_pool)
            self.my_job = the_job
            the_job.my_worker = self

    def update_criminal_tendency(self) -> None:
        """
        This procedure modifies the attribute self.criminal_tendency in-place, based on the individual characteristics of the agent.
        The original nomenclature of the model in Netlogo is: [employment, education, propensity, crim-hist, crim-fam, crim-neigh, oc-member]
        More information on criminal tendency modeling can be found on PROTON-Simulator-Report, page 30, 2.3.2 MODELLING CRIMINAL ACTIVITY (C):
        [https://www.projectproton.eu/wp-content/uploads/2019/10/D5.1-PROTON-Simulator-Report.pdf]
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
                len([agent for agent in self.family_link_neighbors() if agent.num_crimes_committed > 0]) /
                len(self.family_link_neighbors())) > 0.5 else 1.0
        # crim-neigh
        self.criminal_tendency *= 1.81 if self.get_neighbor_list("friendship") or self.get_neighbor_list("professional") and (
                len([agent for agent in self.get_neighbor_list("friendship") if agent.num_crimes_committed > 0]
                    + [agent for agent in self.get_neighbor_list("professional") if agent.num_crimes_committed > 0]) /
                len([agent for agent in self.get_neighbor_list("friendship")] +
                    [agent for agent in self.get_neighbor_list("professional")])) > 0.5 else 1.0
        # oc-member
        self.criminal_tendency *= 4.50 if self.oc_member else 1.0


    def family_link_neighbors(self) -> List[Person]:
        """
        This function returns a list of all agents that have sibling,offspring,partner type connection with the agent.
        :return: List[Person], the agents
        """
        return self.get_neighbor_list("sibling") + self.get_neighbor_list("offspring") + self.get_neighbor_list(
            "partner")

    def remove_from_household(self) -> None:
        """
        This method removes the agent from household, keeping the networks consistent.
        Modify the Person.neighbors attribute in-place
        :return: None
        """
        for member in self.neighbors.get("household").copy():
            if self in member.neighbors.get("household"):
                member.neighbors.get("household").remove(self)
                self.neighbors.get("household").remove(member)

    def leave_school(self) -> None:
        """
        This method modifies in-place the my_school attribute and the School.my_students attribute.
        :return: None
        """
        self.my_school.my_students.remove(self)
        self.my_school = None

    def just_changed_age(self) -> bool:
        """
        If the agent has changed years during this tick this function returns true, otherwise it returns false.
        :return: bool
        """
        return np.floor((self.model.tick - self.birth_tick) / self.model.ticks_per_year) \
               == ((self.model.tick - self.birth_tick) / self.model.ticks_per_year)

    def update_unemployment_status(self) -> None:
        """
        This function modifies the job_level attribute in-place according to table model.labour_status_by_age_and_sex
        :return: None
        """
        self.job_level = 0 if self.model.random.random() < self.model.labour_status_by_age_and_sex[self.gender_is_male][
            self.age] else 1

    def find_accomplices(self, n_of_accomplices: int) -> List[Person]:
        """
        This method is used to find accomplices during commit_crimes procedure
        :param n_of_accomplices: int, number of accomplices
        :return: List[Person]
        """
        if n_of_accomplices == 0:
            offenders_group = [self]
        else:
            d = 1  # start with a network distance of 1
            accomplices = set()
            facilitator_needed = n_of_accomplices >= self.model.threshold_use_facilitators and not self.facilitator
            if facilitator_needed:
                n_of_accomplices -= 1  # save a slot for the facilitator
            while len(accomplices) < n_of_accomplices and d <= self.model.max_accomplice_radius:
                # first create the group
                candidates = sorted(self.agents_at_distance(d), key=lambda x: self.candidates_weight(x))
                while len(accomplices) < n_of_accomplices and len(candidates) > 0:
                    candidate = candidates[0]
                    candidates.remove(candidate)
                    accomplices.add(candidate)
                    # todo: Should be if candidate.facilitator and facilitator_needed? tracked issue #234
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
                    accomplices.add(self.model.random.choice(available_facilitators))
            if len(accomplices) < n_of_accomplices:
                self.model.crime_size_fails += 1
            offenders_group = list(accomplices)
            offenders_group.append(self)
            if n_of_accomplices >= self.model.threshold_use_facilitators:
                if [agent for agent in offenders_group if agent.facilitator]:
                    self.model.facilitator_crimes += 1
                else:
                    self.model.facilitator_fails += 1
        return offenders_group

    def candidates_weight(self, agent: Person) -> float:
        """
        This is what in the paper is called r - this is r R is then operationalised as the proportion
        of OC members among the social relations of each individual (comprising family, friendship, school,
        working and co-offending relations)
        :param agent: Person
        :return: float, the candidates weight
        """
        return -1 * (self.social_proximity(agent) * agent.oc_embeddedness() *
                     agent.criminal_tendency) if self.oc_member \
            else (self.social_proximity(agent) * agent.criminal_tendency)

    def _agents_in_radius(self, context: List[str] =network_names) -> Set[Person]:
        """
        It finds the agents distant 1 in the specified networks, by default it finds it on all networks.
        :param context: List[str], limit to networks name
        :return: Set[Person]
        """
        agents_in_radius = set()
        for net in context:
            if self.neighbors.get(net):
                for agent in self.neighbors.get(net):
                    agents_in_radius.add(agent)
        return agents_in_radius

    def agents_in_radius(self, d: int, context: List[str] =network_names) -> Set[Person]:
        """
        It finds the agents distant "d" or less in the specified networks "context", by default it finds it on all networks.
        :param d: int, the distance
        :param context: List[str], limit to networks name
        :return: Set[Person]
        """
        # todo: This function can be unified to neighbors_range
        rings = [set([self])]
        rings.append(self._agents_in_radius(context))
        if d == 1:
            return rings[1]
        else:
            for i in range(1,d):
                nextring = set().union(*[x._agents_in_radius(context) for x in rings[i]])
                for j in range(i+1):
                    nextring -= rings[j] # removing the previous rings. Takes care of self, too.
                rings.append(nextring)
            summed_rings = set()
            rings.pop(0) # removes the origin agent, the self
            for ring in rings:
                summed_rings = summed_rings.union(ring)
            return summed_rings

    def agents_at_distance(self, d: int, context: List[str] =network_names) -> Set[Person]:
        """
        It finds the agents exactly distant "d" in the specified networks "context", by default it finds it on all networks.
        :param d: int, the distance
        :param context: List[str], limit to networks name
        :return: Set[Person]
        """
        # todo: This function can be unified to neighbors_range
        rings = [set([self])]
        rings.append(self._agents_in_radius(context))
        if d == 1:
            return rings[1]
        else:
            for i in range(1,d):
                nextring = set().union(*[x._agents_in_radius(context) for x in rings[i]])
                for j in range(i+1):
                    nextring -= rings[j] # removing the previous rings. Takes care of self, too.
                rings.append(nextring)
            return nextring

    def oc_embeddedness(self) -> float:
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

    def find_oc_weight_distance(self, agents: Union[Set[Person], List[Person]]) -> float:
        """
        Based on the graph self.model.meta_graph calculates the weighted distance of self from each agent passed to the agents parameter
        :param agents: Union[Set[Person], List[Person]]
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

    def find_oc_distance(self, agents: Union[Set[Person], List[Person]]) -> float:
        """
        Based on the graph self.model.meta_graph calculates the weighted distance of self from each agent passed to the agents parameter
        :param agents: Union[Set[Person], List[Person]]
        :return: float, the distance
        """
        if self in agents:
            agents.remove(self)
        distance = 0
        for agent in agents:
            distance += self.model.meta_graph[self.unique_id][agent.unique_id]["weight"]
        return distance

    def calculate_oc_member_position(self) -> float:
        """
        Calculate the oc-member position of self
        :return: float, the oc-member-position
        """
        n = len([agent for agent in self.agents_in_radius(1) if agent.oc_member])
        my_oc_crim = [agent for agent in self.neighbors.get("criminal") if agent.oc_member]
        return n + np.sum([self.num_co_offenses[agent] for agent in my_oc_crim]) - len(my_oc_crim)

    def get_caught(self) -> None:
        """
        When an agent is caught during a crime and goes to prison, this procedure is activated.
        :return: None
        """
        self.model.number_law_interventions_this_tick += 1
        self.model.people_jailed += 1
        self.prisoner = True
        if self.gender_is_male:
            self.sentence_countdown = extra.pick_from_pair_list(self.model.male_punishment_length, self.model.random)
        else:
            self.sentence_countdown = extra.pick_from_pair_list(self.model.female_punishment_length, self.model.random)
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

    def p_fertility(self) -> float:
        """
        Calculate the fertility
        :return: flot, the fertility
        """
        if np.min([self.number_of_children, 2]) in self.model.fertility_table[self.age]:
            return self.model.fertility_table[self.age][np.min([self.number_of_children, 2])] / self.model.ticks_per_year
        else:
            return 0

    def p_mortality(self) -> float:
        """
        Base on the table self.model.mortality_table calculate a probability that this agent die
        :return: float
        """
        if self.age in self.model.mortality_table:
            p = self.model.mortality_table[self.age][self.gender_is_male] / self.model.ticks_per_year
        elif self.age > max(self.model.mortality_table):
            p = 1
        else:
            raise Exception(self.__repr__() + " age: " + str(self.age) + ", not in mortality table keys")
        return p

    def init_baby(self) -> None:
        """
        This method is for mothers only and allows to create new agents
        :return: None
        """
        self.number_of_children += 1
        self.model.number_born += 1
        new_agent = Person(self.model)
        self.model.schedule.add(new_agent)
        new_agent.wealth_level = self.wealth_level
        new_agent.birth_tick = self.model.tick
        new_agent.mother = self
        if self.get_neighbor_list("offspring"):
            new_agent.add_sibling_link(self.get_neighbor_list("offspring"))
        self.make_parent_offsprings_link(new_agent)
        if self.get_neighbor_list("partner"):
            dad = self.get_neighbor_list("partner")[0]
            dad.make_parent_offsprings_link(new_agent)
            new_agent.father = dad
            new_agent.max_education_level = dad.max_education_level
        else:
            new_agent.max_education_level = self.max_education_level
        new_agent.make_household_link(self.get_neighbor_list("household"))

    def die(self) -> None:
        """
        When an agent dies all his links cease to exist.
        :return: None
        """
        neighbors = self.agents_in_radius(1)
        for agent in neighbors:
            for net in self.network_names:
                if self in agent.neighbors.get(net):
                    agent.neighbors.get(net).remove(self)

    def dump_net(self, network_name: str) -> List[int]:
        """
        Given a @network_name this function returns a list with the unique_id of all agents within
        this network from self.
        :param network_name: str
        :return: List[int]
        """
        if network_name not in self.network_names:
            raise Exception(network_name + " is not a valid network name")
        return [agent.unique_id for agent in self.neighbors.get(network_name)]

    def social_proximity(self, target: Person) -> int:
        """
        This function calculates the social proximity between self and another agent based on age,
        gender, wealth level, education level and friendship
        :param target: Person
        :return: int, social proximity
        """
        #todo: add weight? we could create a global model attribute(a dict) with weights
        total = 0
        total += 0 if abs(target.age - self.age) > 18 else 1 - abs(target.age - self.age)/18
        total += 1 if self.gender_is_male == target.gender_is_male else 0
        total += 1 if self.wealth_level == target.wealth_level else 0
        total += 1 if self.education_level == target.education_level else 0
        total += 1 if self.neighbors.get("friendship").intersection(
            target.neighbors.get("friendship")) else 0
        return total

    def n_links(self):
        result = 0
        for net in self.network_names:
            result += len(self.neighbors.get(net))
        return result


class Job:

    def __init__(self, model: ProtonOC):
        self.model: ProtonOC = model
        self.job_level: int = 0
        self.my_employer: Union[Employer, None] = None
        self.my_worker: Union[Person, None] = None
        self.unique_id: int = model.max_ids["job"]
        model.max_ids["job"] += 1

    def __repr__(self):
        return "Job: " + str(self.unique_id) + " Level: " + str(self.job_level)


class Employer:

    def __init__(self, model: ProtonOC):
        self.my_jobs: List = list()
        self.model: ProtonOC = model
        self.unique_id: int = model.max_ids["employer"]
        model.max_ids["employer"] += 1

    def __repr__(self) -> str:
        return "Employer: " + str(self.unique_id)

    def create_job(self, level: int, worker: Person) -> None:
        """
        This function creates new jobs and assigns a @level and a @worker.
        :param level: int, the job level
        :param worker: Person, the worker
        :return: None
        """
        newjob = Job(self.model)
        newjob.level = level
        worker.my_job = newjob
        self.my_jobs.append(newjob)

    def employees(self) -> List[Person]:
        """
        This function returns employees related to this employer
        :return: List[Person]
        """
        return [x.my_worker for x in self.my_jobs if x.my_worker != None]


class School:

    def __init__(self, model: ProtonOC, diploma_level: int):
        self.model: ProtonOC = model
        self.diploma_level: int = diploma_level
        self.my_students: Set[Person] = set()
        self.unique_id: int = model.max_ids["school"]
        model.max_ids["school"] += 1

    def __repr__(self):
        return "School: " + str(self.unique_id) + " Level: " + str(self.diploma_level)

if __name__ == "__main__":
    pass
