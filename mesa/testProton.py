# that's strange - at somepoint it always failed the first run after changing something, then no more
import pytest
from mesaPROTON_OC import MesaPROTON_OC
import Person as pp
import numpy as np


def test_random():
    """
    Tests the random generation of numbers through the two modules (numpy random and random) with a single seed.
    """
    model = MesaPROTON_OC(seed=42)
    assert model.check_random == [0.7739560485559633, 0.6394267984578837]

# def test_networks():
#     pp.Person.persons = []
#     # testing link exploration
#     links = [[4, 5], [2, 3], [1], [1, 8], [0, 6, 5, 7], [4, 0], [4], [4, 8], [9, 3, 8], [8]]
#     m = MesaPROTON_OC()
#     for i in range(0, 10):
#         pp.Person(m)
#     for i in range(0, 10):
#         for l in links[i]: pp.Person.persons[i].neighbors.get('friendship').add(pp.Person.persons[l])
#     # for i in range(0,10):
#     #     print([x.unique_id for x in pp.Person.persons[i].neighbors.get('friendship')])
#     ne = pp.Person.persons[5].neighbors_range('friendship', 3)
#     assert sorted([x.unique_id for x in ne]) == [0, 4, 6, 7, 8]
#     # print([x.unique_id for x in ne]) # should be [ 4, 7, 8, 0, 6]
#
# def test_generate_households():
#     """
#     test the households generation
#     1. Check if all families have been generated
#     2. Take a random household and check if all the members of the household are in the other members' network
#     3. Take the first simple family (we're sure it's in the first 5) and check if all the networks work.
#     4. wealth must be the same for all members of the household
#     5. nobody should have more than one father and one mather
#     """
#     m = MesaPROTON_OC()
#     m.initial_agents = 1000
#     m.create_agents()
#     m.generate_households()
#     #1
#     counter_couple = 0
#     counter_single_parent = 0
#     for family in m.families:
#         if family[0].neighbors["partner"]:
#             counter_couple += 1
#         else:
#             counter_single_parent += 1
#     single = len([x for x in m.hh_size if x == 1])
#     assert counter_couple+counter_single_parent+single == len(m.hh_size)
#     #2
#     test_family = m.rng.choice(m.families)
#     for member in test_family:
#         other_members = set([x for x in test_family if x != member])
#         assert other_members == member.neighbors["household"]
#     #3
#     for test_simple_family in m.families[:5]:
#         if len(test_simple_family) >= 3 and test_family[0].neighbors["partner"] == test_family[1] and test_family[1].neighbors["partner"]  == test_family[0]:
#             assert set(test_simple_family[1:]) == test_simple_family[0].neighbors["household"]
#             assert test_simple_family[-1] in test_simple_family[0].neighbors["offspring"]
#             assert test_simple_family[-1] in test_simple_family[1].neighbors["offspring"]
#             if type(test_simple_family[2:]) == list:
#                 for son in test_simple_family[2:]:
#                     assert son.neighbors["parent"] == set(test_simple_family[:2])
#             else:
#                 assert test_simple_family[-1].neighbors["parent"] == set(test_simple_family[:2])
#     #4
#     for agent in m.schedule.agents:
#         for household in agent.neighbors["household"]:
#             assert agent.wealth_level == household.wealth_level
#     #5
#     for agent in m.schedule.agents:
#         if agent.neighbors["parent"]:
#             assert len(agent.neighbors["parent"]) <= 2
#             assert len([x for x in agent.neighbors["parent"] if x.gender_is_male == True]) <= 1
#             assert len([x for x in agent.neighbors["parent"] if x.gender_is_male == False]) <= 1
#
# def test_weddings():
#     model = MesaPROTON_OC()
#     model.setup(1000)
#     initial_wedding = len([x for x in model.schedule.agents if x.get_link_list("partner")])
#     for tick in range(100):
#         model.step()
#     for agent in model.schedule.agents:
#         if agent.get_link_list("partner"):
#             assert agent.get_link_list("partner")[0].get_link_list("partner")[0] == agent
#     assert model.number_weddings == (len([x for x in model.schedule.agents if x.get_link_list("partner")]) - initial_wedding) / 2
#     assert model.number_weddings > 0
#     # coherent state of weddings
#
# def test_inflate_deflate_network():
#     m = MesaPROTON_OC()
#     m.create_agents(random_relationships=True)
#     tot_links = m.total_num_links()
#     assert tot_links
#
# def test_oc_creation():
#     m = MesaPROTON_OC()
#     m.initial_agents = 500
#     m.create_agents()
#     m.number_weddings_mean = 1000
#     for i in range(1, 5):
#         m.wedding()
#     # todo: fix this routine
#     # m.setup_oc_groups()
#     # print(m.total_num_links())

def test_big_crimes_from_small_fish():
    """
    A large crime organized by a small fish is reported
    :return: None
    """
    model = MesaPROTON_OC(as_netlogo=True)
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
    model = MesaPROTON_OC(as_netlogo=True)
    model.setup(1000)
    for agent in model.schedule.agents:
        if agent.neighbors.get("criminal"):
            for criminal in agent.neighbors.get("criminal"):
                assert agent.num_co_offenses[criminal] >= 1

def test_oc_crime_stats():
    model = MesaPROTON_OC(as_netlogo=True)
    model.setup(1500)
    for n in range(20):
        model.step()
        for cell, value in model.c_range_by_age_and_sex:
            pool = [agent for agent in model.schedule.agents
                if agent.age() > cell[1] and agent.age() <= value[0] and agent.gender_is_male]
            if pool and np.sum([agent.num_crimes_committed for agent in pool]) > 0:
                result = np.abs(value[1]) * model.ticks / model.ticks_per_year \
                - np.mean([agent.num_crimes_committed for agent in pool]) < \
                2 * np.std([agent.num_crimes_committed for agent in pool])
                assert result

def test_oc_embeddedness():
    def test1(model):
        """
        A single non-OC person
        :param model: the model
        :return: None
        """
        agent = pp.Person(model)
        assert agent.oc_embeddedness() == 0

    def test2(model):
        """
        A single non-OC person with one family OC member
        :param mdoel: the model
        :return: None
        """
        agent1 = pp.Person(model)
        agent2 = pp.Person(model)
        agent2.oc_member = True
        agent1.addSiblingLinks([agent2])
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
            agent = pp.Person(model)
            pool.append(agent)
        father = model.rng.choice(pool)
        pool.remove(father)
        for agent in list(model.rng.choice(pool, size=5, replace=False)):
            agent.oc_member = True
        father.makeParent_OffspringsLinks(pool)
        assert father.oc_embeddedness() == 0.5
        distances = list()
        for agent in pool:
            distances.append(father.find_oc_distance([agent]))
        assert distances == list(np.full(10,1))

    def test4(model):
        """
        A non-OC person with one double link to an OC member
        :param model: The model
        :return: None
        """
        pool = list()
        for i in range(3):
            agent = pp.Person(model)
            pool.append(agent)
        pool[2].oc_member = True
        pool[0].addSiblingLinks([pool[1]])
        pool[0].makePartnerLinks(pool[2])
        pool[0].makeFriends(pool[2])
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
            agent = pp.Person(model)
            pool.append(agent)
        pool[2].oc_member = True
        pool[0].makePartnerLinks(pool[1])
        pool[0].makeFriends(pool[1])
        pool[0].makeFriends(pool[2])
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
            agent = pp.Person(model)
            pool.append(agent)
        pool[0].addSiblingLinks([pool[1]])
        pool[0].makeParent_OffspringsLinks(pool[2])
        pool[0].addCriminalLink(pool[2])
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
            agent = pp.Person(model)
            pool.append(agent)

        pool[0].makePartnerLinks(pool[1])
        pool[0].makeFriends(pool[2])
        pool[0].makeProfessionalLinks(pool[3])
        pool[0].makeSchoolLinks(pool[4])
        pool[0].addCriminalLink(pool[5])
        pool[0].num_co_offenses[pool[5]] = 5
        pool[5].num_co_offenses[pool[0]] = 5
        pool[0].makeParent_OffspringsLinks(pool[5])
        pool[5].oc_member = True

        assert pool[0].oc_embeddedness() == 0.6
        distances = list()
        for agent in pool[1:]:
            distances.append(pool[0].find_oc_distance([agent]))
        assert sorted(distances) == [1/6, 1.0, 1.0, 1.0, 1.0]


    #Test
    model = MesaPROTON_OC(as_netlogo=True)
    model.setup(1000)
    test1(model) # A single non-OC person
    test2(model) # A single non-OC person with one family OC member
    test3(model) # A non-OC person with its family being OC member
    test4(model) # A non-OC person with one double link to an OC member
    test5(model) # A non-OC person with one double link to a non-OC member
    test6(model) # A non-OC person with a strong co-offending link to an OC member
    test7(model) # A non-OC person with all types of links










# def test_population_generator():
#     m = MesaPROTON_OC()
#     m.initial_agents = 2000
#     m.load_stats_tables()
#     m.facilitator_fails = 0
#     m.facilitator_crimes = 0
#     m.setup_persons_and_friendship()
#     pass