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


from model import ProtonOC
from entities import Person
import numpy as np
import extra
import os
import sys
import pytest


def test_generate_households():
    """
    test the households generation
    1. Check if all families have been generated
    2. Take a random household and check if all the members of the household are in the other members' network
    3. Take the first simple family (we're sure it's in the first 5) and check if all the networks work.
    4. wealth must be the same for all members of the household
    5. nobody should have more than one father and one mother
    """
    model = ProtonOC()
    model.initial_agents = 1000
    model.setup_education_levels()
    model.setup_persons_and_friendship()
    model.setup_schools()
    model.init_students()
    model.assign_jobs_and_wealth()
    model.setup_inactive_status()
    model.generate_households()
    #1
    counter_couple = 0
    counter_single_parent = 0
    for family in model.families:
        if family[0].neighbors["partner"]:
            counter_couple += 1
        else:
            counter_single_parent += 1
    single = len([x for x in model.hh_size if x == 1])
    assert counter_couple+counter_single_parent+single == len(model.hh_size)
    #2
    test_family = model.random.choice(np.array(model.families, dtype=object))
    for member in test_family:
        other_members = set([x for x in test_family if x != member])
        assert other_members == member.neighbors["household"]
    #3
    for test_simple_family in model.families:
        if len(test_simple_family) >= 3 and test_family[0].neighbors["partner"] == test_family[1] and test_family[1].neighbors["partner"]  == test_family[0]:
            assert set(test_simple_family[1:]) == test_simple_family[0].neighbors["household"]
            assert test_simple_family[-1] in test_simple_family[0].neighbors["offspring"]
            assert test_simple_family[-1] in test_simple_family[1].neighbors["offspring"]
            for son in test_simple_family[2:]:
                assert son.neighbors["parent"] == set(test_simple_family[:2])
    #4
    for agent in model.schedule.agents:
        for household in agent.neighbors["household"]:
            assert agent.wealth_level == household.wealth_level
    #5
    for agent in model.schedule.agents:
        if agent.neighbors["parent"]:
            assert len(agent.neighbors["parent"]) <= 2
            assert len([x for x in agent.neighbors["parent"] if x.gender_is_male is True]) <= 1
            assert len([x for x in agent.neighbors["parent"] if x.gender_is_male is False]) <= 1


def test_weddings():
    """
    Coherent state of weddings
    :return: None
    """
    model = ProtonOC()
    model.setup(500)
    initial_wedding = len([x for x in model.schedule.agents if x.get_neighbor_list("partner")])
    for tick in range(100):
        model.wedding()
    for agent in model.schedule.agents:
        if agent.get_neighbor_list("partner"):
            assert agent.get_neighbor_list("partner")[0].get_neighbor_list("partner")[0] == agent
    assert model.number_weddings * 2 == (len([x for x in model.schedule.agents if x.get_neighbor_list("partner")]) - initial_wedding)
    assert model.number_weddings > 0


def test_big_crimes_from_small_fish():
    """
    A large crime organized by a small fish is reported
    :return: None
    """
    model = ProtonOC()
    model.max_accomplice_radius = 6
    model.setup(500)
    model.num_co_offenders_dist = [[5, 0.5], [6, 0.5], [10, 0.5]]
    for tick in range(20):
        model.step()
    assert model.big_crime_from_small_fish > 0


def test_oc_crime_net_init():
    """
    All OC links have weight >= 1
    :return: None
    """
    model = ProtonOC()
    model.setup(1000)
    for agent in model.schedule.agents:
        if agent.neighbors.get("criminal"):
            for criminal in agent.neighbors.get("criminal"):
                assert agent.num_co_offenses[criminal] >= 1


def test_oc_crime_stats():
    model = ProtonOC()
    model.setup(1500)
    for n in range(20):
        model.step()
        for cell, value in model.c_range_by_age_and_sex:
            pool = [agent for agent in model.schedule.agents
                    if agent.age > cell[1] and agent.age <= value[0] and agent.gender_is_male]
            if pool and np.sum([agent.num_crimes_committed for agent in pool]) > 0:
                result = np.abs(value[1]) * model.tick / model.ticks_per_year \
                         - np.mean([agent.num_crimes_committed for agent in pool]) < \
                         2 * np.std([agent.num_crimes_committed for agent in pool])
                assert result


def test_oc_embeddedness():
    """
    Tests oc_embeddedness in various contexts
    :return: None
    """
    def test1(model):
        """
        A single non-OC person
        :param model: the model
        :return: None
        """
        agent = Person(model)
        assert agent.oc_embeddedness() == 0

    def test2(model):
        """
        A single non-OC person with one family OC member
        :param model: the model
        :return: None
        """
        agent1 = Person(model)
        agent2 = Person(model)
        agent2.oc_member = True
        agent1.add_sibling_link([agent2])
        assert agent1.oc_embeddedness() == 1
        assert agent1.find_oc_distance([agent2]) == 1

    def test3(model):
        """
        A non-OC person with its family being OC member
        :param model: the model
        :return: None
        """
        pool = list()
        for i in range(11):
            agent = Person(model)
            pool.append(agent)
        father = model.random.choice(pool)
        pool.remove(father)
        for agent in list(model.random.choice(pool, size=5, replace=False)):
            agent.oc_member = True
        father.make_parent_offsprings_link(pool)
        assert father.oc_embeddedness() == 0.5
        distances = list()
        for agent in pool:
            distances.append(father.find_oc_distance([agent]))
        assert distances == list(np.full(10, 1))

    def test4(model):
        """
        A non-OC person with one double link to an OC member
        :param model: The model
        :return: None
        """
        pool = list()
        for i in range(3):
            agent = Person(model)
            pool.append(agent)
        pool[2].oc_member = True
        pool[0].add_sibling_link([pool[1]])
        pool[0].make_partner_link(pool[2])
        pool[0].make_friendship_link(pool[2])
        assert pool[0].oc_embeddedness() == 2 / 3
        distances = list()
        for agent in pool[1:]:
            distances.append(pool[0].find_oc_distance([agent]))
        assert sorted(distances) == [0.5, 1.0]

    def test5(model):
        """
        A non-OC person with one double link to a non-OC member
        :param model: The model
        :return: None
        """
        pool = list()
        for i in range(3):
            agent = Person(model)
            pool.append(agent)
        pool[2].oc_member = True
        pool[0].make_partner_link(pool[1])
        pool[0].make_friendship_link(pool[1])
        pool[0].make_friendship_link(pool[2])
        assert pool[0].oc_embeddedness() == 1 / 3
        distances = list()
        for agent in pool[1:]:
            distances.append(pool[0].find_oc_distance([agent]))
        assert sorted(distances) == [0.5, 1.0]

    def test6(model):
        """
        A non-OC person with a strong co-offending link to an OC member
        :param model: The model
        :return: None
        """
        pool = list()
        for i in range(3):
            agent = Person(model)
            pool.append(agent)
        pool[0].add_sibling_link([pool[1]])
        pool[0].make_parent_offsprings_link(pool[2])
        pool[0].add_criminal_link(pool[2])
        pool[0].num_co_offenses[pool[2]] = 4
        pool[2].num_co_offenses[pool[0]] = 4
        pool[2].oc_member = True
        assert pool[0].oc_embeddedness() == 5 / 6
        distances = list()
        for agent in pool[1:]:
            distances.append(pool[0].find_oc_distance([agent]))
        assert sorted(distances) == [0.2, 1.0]

    def test7(model):
        """
        A non-OC person with all types of links
        :param model: The model
        :return: None
        """
        pool = list()
        for i in range(6):
            agent = Person(model)
            pool.append(agent)

        pool[0].make_partner_link(pool[1])
        pool[0].make_friendship_link(pool[2])
        pool[0].make_professional_link(pool[3])
        pool[0].make_school_link(pool[4])
        pool[0].add_criminal_link(pool[5])
        pool[0].num_co_offenses[pool[5]] = 5
        pool[5].num_co_offenses[pool[0]] = 5
        pool[0].make_parent_offsprings_link(pool[5])
        pool[5].oc_member = True

        assert pool[0].oc_embeddedness() == 0.6
        distances = list()
        for agent in pool[1:]:
            distances.append(pool[0].find_oc_distance([agent]))
        assert sorted(distances) == [1/6, 1.0, 1.0, 1.0, 1.0]


    #Test
    model = ProtonOC()
    model.setup(1000)
    test1(model)  # A single non-OC person
    test2(model)  # A single non-OC person with one family OC member
    test3(model)  # A non-OC person with its family being OC member
    test4(model)  # A non-OC person with one double link to an OC member
    test5(model)  # A non-OC person with one double link to a non-OC member
    test6(model)  # A non-OC person with a strong co-offending link to an OC member
    test7(model)  # A non-OC person with all types of links


def test_oc_intervention():

    def test1():
        """
        Test the Intervention on OC families
        :return: None
        """
        model = ProtonOC()
        model.setup(550)
        for agent in model.schedule.agents:
            agent.oc_member = False
        agelist = np.arange(0, 12 * 4, 4)
        kingpin = Person(model)
        kingpin.birth_tick = -1 * model.ticks_per_year * 50
        kingpin.oc_member = True
        kingpin.gender_is_male = True
        model.schedule.add(kingpin)
        the_family = list()
        for i in range(12):
            new_agent = Person(model)
            new_agent.father = kingpin
            the_family.append(new_agent)
            model.schedule.add(new_agent)
            age = model.random.choice(np.arange(agelist.size))
            new_agent.birth_tick = -1 * agelist[age] * model.ticks_per_year
            new_agent.calculate_age()
            agelist = np.delete(agelist, age)
            new_agent.propensity = 0
            new_agent.gender_is_male = True
            kingpin.make_parent_offsprings_link(new_agent)
        for agent in the_family:
            agent.add_sibling_link(the_family)
        baby = [agent for agent in the_family if agent.age == 0]
        model.targets_addressed_percent = 100
        model.family_intervention = "remove-if-OC-member"
        model.family_intervene()

        assert np.sum([len(agent.neighbors.get("friendship")) for agent in the_family]) >= 40
        assert len(extra.weighted_one_of(model.schedule.agents, lambda x: x.age == 16 and x.propensity == 0,
                                         model.random).neighbors.get("sibling")) == 11
        assert len([agent for agent in baby[0].neighbors.get("sibling") if agent.my_job is not None]) == 8
        assert np.sum([agent.max_education_level for agent in the_family]) == 8

    def test2():
        """
        Test Educational intervention
        :return: None
        """
        def target_educational():
            """
            Get the mean of max_education_level
            :return: float
            """
            return np.mean([agent.max_education_level for agent in model.schedule.agents
                            if agent.age <= 18 and agent.age >= 12 and agent.my_school is not None])

        def target_psychological():
            """
            Get the sum of friends
            :return: int
            """
            return np.sum([len(agent.neighbors.get("friendship")) for agent in model.schedule.agents
                           if agent.age <= 18 and agent.age >= 12 and agent.my_school is not None])

        model = ProtonOC()
        model.setup(1000)
        model.targets_addressed_percent = 0
        for i in range(5):
            model.step()
        model.social_support = "educational"
        model.ticks_between_intervention = 2
        model.targets_addressed_percent = 20

        #Test Educational
        before = target_educational()
        for i in range(10):
            model.socialization_intervene()
        after = target_educational()
        assert after > before

        #Test psychological
        model.social_support = "psychological"
        before = target_psychological()
        for i in range(10):
            model.socialization_intervene()
        after = target_psychological()
        assert after > before

        #Test target_psychological()
        model.social_support = "more-friends"
        before = target_psychological()
        for i in range(10):
            model.socialization_intervene()
        after = target_psychological()
        assert after > before

    test1()  # Test the Intervention on OC families
    test2()  # Test Educational intervention


def test_oc_job():
    """
    Work system stays coherent
    :return: None
    """
    model = ProtonOC()
    model.migration_on = False
    model.setup(1000)
    for i in range(36):
        model.step()
        # No minor working
        assert any([agent for agent in model.schedule.agents if agent.age < 16 and agent.my_job is not None]) is False
        # Unemployed stay so
        assert any([agent for agent in model.schedule.agents if (agent.job_level == 1 or agent.job_level) == 0 and agent.my_job is not None]) is False
        # Nobody has two jobs
        assert len([agent for agent in model.schedule.agents if agent.my_job is not None]) == len([job for job in model.jobs if job.my_worker is not None])


def test_oc_retirement():
    """
    Old people do not have a job, Young people are not retired, Retired people are old
    note that persons have a birth tick, not an age (age is a reporter)
    thus, after the tick, a person can be just turned 65 but not retired yet (it will be after the go)
    that's why we use age > retirement-age and not >=. During runtime the inequalities are different from the `setup` case because tick
    happens at the end of `go`, so I can be 49 at time of retire-check and 50 at time of report
    :return: None
    """
    model = ProtonOC()
    model.migration_on = False
    model.retirement_age = 65
    model.setup(100)
    assert len([agent for agent in model.schedule.agents
                if agent.age >= model.retirement_age and agent.neighbors.get("professional")]) == 0
    assert len([agent for agent in model.schedule.agents
                if agent.age < model.retirement_age and agent.retired]) == 0
    assert len([agent for agent in model.schedule.agents
                if agent.age >= model.retirement_age and not agent.retired]) == 0

    for i in range(20):
        model.step()
        assert len([agent for agent in model.schedule.agents
                    if agent.age > model.retirement_age and agent.neighbors.get("professional")]) == 0
        assert len([agent for agent in model.schedule.agents
                    if agent.age < model.retirement_age and agent.retired]) == 0
        assert len([agent for agent in model.schedule.agents
                    if agent.age > model.retirement_age and not agent.retired]) == 0


def test_school():
    """
    Check the correct status of schools and students during setup and during runtime
    :return: None
    """
    def possible_school_level(model, agent):
        """
        Get the expected school level of the agent
        :param model: The model
        :param agent: The agent
        :return: int, the expected school level
        """
        for level in model.education_levels:
            if agent.age <= model.education_levels[level][1] \
                    and agent.age >= model.education_levels[level][0]:
                the_level = level
                return the_level

    def assertions(model, agent):
        """
        List of assertions that are performed on every agents
        :param model: The model
        :param agent: The agent
        :return: None
        """
        expected_school_level = possible_school_level(model, agent)
        #1 There must be no agents who work and go to school
        assert not (agent.my_school is not None and agent.my_job is not None)
        if agent.my_school:
            #2 No agent acquires the level of education before finishing school
            assert agent.education_level == agent.my_school.diploma_level - 1
            #3 All agents who go to school at a certain level respect age limits
            assert agent.my_school.diploma_level == expected_school_level and agent.education_level == expected_school_level - 1
            #4 The agent who goes to that school must be in the students of that school
            assert agent in agent.my_school.my_students
            #5 The agent who goes to that school must be in the students of that school
            assert agent.my_school in model.schools
            #6 The agent can only be found among students at a single school
            assert len([school for school in model.schools if agent in school.my_students]) == 1


    model = ProtonOC()
    model.setup(500)
    for agent in model.schedule.agents:
        assertions(model, agent)
    for i in range(36):
        for agent in model.schedule.agents:
            assertions(model, agent)

def test_determinism():
    """
    Check if two simulations with the same seed give the same results.
    """
    def check_differences(a_model, another_model):
        """
        Given 2 model instance (a_model and another_model), this function check for:
        """
        network_names = ['sibling', 'offspring', 'parent', 'partner', 'household', 'friendship',
                         'criminal', 'professional', 'school']
        # 1. education level for all agents
        assert [agent.education_level for agent in a_model.schedule.agents] \
               == [agent.education_level for agent in another_model.schedule.agents]
        # 2. max_education level for all agents
        assert [agent.max_education_level for agent in a_model.schedule.agents] \
               == [agent.max_education_level for agent in another_model.schedule.agents]
        # 3. Initial network adges
        assert list(a_model.watts_strogatz.edges) == list(another_model.watts_strogatz.edges)
        # 4. education_levels table
        assert a_model.education_levels == another_model.education_levels
        # 5. Age of all agents
        assert [agent.age for agent in a_model.schedule.agents] == [agent.age for agent in
                                                                 another_model.schedule.agents]
        # 5. birth_tick of all agents
        assert [agent.birth_tick for agent in a_model.schedule.agents] == [agent.birth_tick for agent in
                                                                      another_model.schedule.agents]
        # 6. wealth_level of all agents
        assert [agent.wealth_level for agent in a_model.schedule.agents] == [agent.wealth_level for agent
                                                                        in another_model.schedule.agents]
        # 7. propensity of all agents
        assert [agent.propensity for agent in a_model.schedule.agents] == [agent.propensity for agent in
                                                                      another_model.schedule.agents]
        # 8. hobby of all agents
        assert [agent.hobby for agent in a_model.schedule.agents] == [agent.hobby for agent in
                                                                   another_model.schedule.agents]
        # 9. gender of all agents
        assert [agent.gender_is_male for agent in a_model.schedule.agents] == [agent.gender_is_male for
                                                                          agent
                                                                          in
                                                                          another_model.schedule.agents]
        # 10. unique_id of all_agents
        assert [school.unique_id for school in a_model.schools] == [school.unique_id for school in
                                                                 another_model.schools]
        # 11. diploma level of all agents
        assert [school.diploma_level for school in a_model.schools] == [school.diploma_level for school
                                                                     in
                                                                     another_model.schools]
        # 12. students of all schools
        for school1, school in zip(another_model.schools, a_model.schools):
            assert  set([agent.unique_id for agent in school1.my_students]) == set([agent.unique_id for
                                                                               agent in
                                                                               school.my_students])
        # 13. all network of all agents
        for net in network_names:
            for agent, agent1 in zip(a_model.schedule.agents, another_model.schedule.agents):
                if agent.neighbors.get(net) and agent1.neighbors.get(net):
                    assert  set([agent.unique_id for agent in agent.neighbors.get(net)]) == set([
                        agent.unique_id
                        for agent in
                        agent1.neighbors.get(net)])

        # 14. syncronization of the default_rng instace
        assert a_model.random.random() == another_model.random.random()

    common_seed = int.from_bytes(os.urandom(4), sys.byteorder)
    a_model = ProtonOC(seed=common_seed)
    a_model.intervention = "baseline"
    a_model.setup(n_agents=1000)

    another_model = ProtonOC(seed=common_seed)
    another_model.intervention = "baseline"
    another_model.setup(n_agents=1000)

    # check setup
    check_differences(a_model, another_model)

    for i in range(200):
        a_model.step()
        another_model.step()

    #check step
    check_differences(a_model, another_model)

def test_micro_net():

    def generate_micro_net(model):
        for i in range(18):
            new_agent = Person(model)
            model.schedule.add(new_agent)
            new_agent.oc_member = False
            new_agent.facilitator = False
            new_agent.gender_is_male = i % 2 == 0
            new_agent.target_of_intervention = False
            new_agent.age = i * 149 % 45 + 10
            new_agent.education_level = i * 149 % 4
            new_agent.criminal_tendency = i * 149 % 100 / 100
            new_agent.wealth_level = i * 149 % 4
            new_agent.job_level = i * 149 % 4
            new_agent.propensity = i * 149 % 100 / 100
            new_agent.migrant = i % 3 == 0

        model.schedule.agents[0].make_partner_link(model.schedule.agents[1])
        model.schedule.agents[0].make_friendship_link(model.schedule.agents[2])
        model.schedule.agents[0].make_professional_link(model.schedule.agents[3])
        model.schedule.agents[0].make_school_link(model.schedule.agents[4])
        model.schedule.agents[0].add_criminal_link(model.schedule.agents[5])
        model.schedule.agents[0].num_co_offenses[model.schedule.agents[5]] = 5
        model.schedule.agents[5].num_co_offenses[model.schedule.agents[0]] = 5
        model.schedule.agents[5].make_parent_offsprings_link(model.schedule.agents[0])

        model.schedule.agents[6].make_friendship_link(model.schedule.agents[5])
        model.schedule.agents[7].make_partner_link(model.schedule.agents[8])
        model.schedule.agents[8].make_friendship_link(model.schedule.agents[9])
        model.schedule.agents[7].make_parent_offsprings_link(model.schedule.agents[9])
        model.schedule.agents[10].make_professional_link(model.schedule.agents[9])
        model.schedule.agents[10].make_professional_link(model.schedule.agents[11])
        model.schedule.agents[10].make_school_link(model.schedule.agents[13])

        model.schedule.agents[11].make_professional_link(model.schedule.agents[12])
        model.schedule.agents[12].make_professional_link(model.schedule.agents[13])
        model.schedule.agents[12].make_professional_link(model.schedule.agents[14])
        model.schedule.agents[12].make_professional_link(model.schedule.agents[16])

        model.schedule.agents[13].make_friendship_link(model.schedule.agents[15])
        model.schedule.agents[14].make_professional_link(model.schedule.agents[15])

        model.schedule.agents[14].make_household_link([model.schedule.agents[17]])
        model.schedule.agents[16].make_household_link([model.schedule.agents[12]])
        model.schedule.agents[16].make_household_link([model.schedule.agents[17]])

        model.schedule.agents[5].oc_member = True
        model.schedule.agents[17].oc_member = True
        model.schedule.agents[9].facilitator = True
        model.schedule.agents[3].facilitator = True

    model = ProtonOC()
    generate_micro_net(model)

    #tests that agents_at_distance isn't broken.
    ag_9_range_3 = set().union(
        [model.schedule.agents[x] for x in [12,15]])

    ag_0_range_2 = set([model.schedule.agents[6]])

    assert model.schedule.agents[0].agents_at_distance(2)==ag_0_range_2
    assert model.schedule.agents[9].agents_at_distance(3)==ag_9_range_3

    #tests that agents_in_radius isn't broken.
    ag_9_range_3 = list()
    for i in [7,8,10,11,12,13,15]:
        ag_9_range_3.append(model.schedule.agents[i])
    ag_9_range_3 = set(ag_9_range_3)

    ag_0_range_2 = list()
    for i in [1,2,3,4,5,6]:
        ag_0_range_2.append(model.schedule.agents[i])
    ag_0_range_2 = set(ag_0_range_2)

    assert model.schedule.agents[0].agents_in_radius(2)==ag_0_range_2
    assert model.schedule.agents[9].agents_in_radius(3)==ag_9_range_3


    #test if the trouble starter is the last of the accomplices list
    assert model.schedule.agents[0].find_accomplices(5)[-1] == model.schedule.agents[0]

