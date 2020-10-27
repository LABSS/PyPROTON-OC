# that's strange - at somepoint it always failed the first run after changing something, then no more
import pytest
from mesaPROTON_OC import MesaPROTON_OC
import Person as pp


def test_random():
    """
    Tests the random generation of numbers through the two modules (numpy random and random) with a single seed.
    """
    m = MesaPROTON_OC(seed=42)
    assert m.check_random == [0.7739560485559633, 0.6394267984578837]

def test_networks():
    pp.Person.persons = []
    # testing link exploration
    links = [[4, 5], [2, 3], [1], [1, 8], [0, 6, 5, 7], [4, 0], [4], [4, 8], [9, 3, 8], [8]]
    m = MesaPROTON_OC()
    for i in range(0, 10):
        pp.Person(m)
    for i in range(0, 10):
        for l in links[i]: pp.Person.persons[i].neighbors.get('friendship').add(pp.Person.persons[l])
    # for i in range(0,10):
    #     print([x.unique_id for x in pp.Person.persons[i].neighbors.get('friendship')])
    ne = pp.Person.persons[5].neighbors_range('friendship', 3)
    assert sorted([x.unique_id for x in ne]) == [0, 4, 6, 7, 8]
    # print([x.unique_id for x in ne]) # should be [ 4, 7, 8, 0, 6]

def test_generate_households():
    """
    test the households generation
    1. Check if all families have been generated
    2. Take a random household and check if all the members of the household are in the other members' network
    3. Take the first simple family (we're sure it's in the first 5) and check if all the networks work.
    4. wealth must be the same for all members of the household
    5. nobody should have more than one father and one mather
    """
    m = MesaPROTON_OC()
    m.initial_agents = 1000
    m.create_agents()
    m.generate_households()
    #1
    counter_couple = 0
    counter_single_parent = 0
    for family in m.families:
        if family[0].neighbors["partner"]:
            counter_couple += 1
        else:
            counter_single_parent += 1
    single = len([x for x in m.hh_size if x == 1])
    assert counter_couple+counter_single_parent+single == len(m.hh_size)
    #2
    test_family = m.rng.choice(m.families)
    for member in test_family:
        other_members = set([x for x in test_family if x != member])
        assert other_members == member.neighbors["household"]
    #3
    for test_simple_family in m.families[:5]:
        if len(test_simple_family) >= 3 and test_family[0].neighbors["partner"] == test_family[1] and test_family[1].neighbors["partner"]  == test_family[0]:
            assert set(test_simple_family[1:]) == test_simple_family[0].neighbors["household"]
            assert test_simple_family[-1] in test_simple_family[0].neighbors["offspring"]
            assert test_simple_family[-1] in test_simple_family[1].neighbors["offspring"]
            if type(test_simple_family[2:]) == list:
                for son in test_simple_family[2:]:
                    assert son.neighbors["parent"] == set(test_simple_family[:2])
            else:
                assert test_simple_family[-1].neighbors["parent"] == set(test_simple_family[:2])
    #4
    for agent in m.schedule.agents:
        for household in agent.neighbors["household"]:
            assert agent.wealth_level == household.wealth_level
    #5
    for agent in m.schedule.agents:
        if agent.neighbors["parent"]:
            assert len(agent.neighbors["parent"]) <= 2
            assert len([x for x in agent.neighbors["parent"] if x.gender_is_male == True]) <= 1
            assert len([x for x in agent.neighbors["parent"] if x.gender_is_male == False]) <= 1

def test_weddings():
    m = MesaPROTON_OC()
    m.initial_agents = 500
    m.create_agents(random_relationships=True, exclude_partner_net=True)
    print(len(m.schedule.agents) - len(pp.Person.persons))
    print(m.number_weddings)
    m.number_weddings_mean = 100
    for i in range(1, 2):
        m.wedding()
    # print(Person.NumberOfLinks()-l)
    for agent in m.schedule.agents:
        if agent.get_neighbor_list("partner"):
            assert agent.get_neighbor_list("partner")[0].get_neighbor_list("partner")[0] == agent
    assert m.number_weddings == len([x for x in m.schedule.agents if x.get_neighbor_list("partner")]) / 2
    assert m.number_weddings > 0
    # coherent state of weddings

def test_inflate_deflate_network():
    m = MesaPROTON_OC()
    m.create_agents(random_relationships=True)
    tot_links = m.total_num_links()
    assert tot_links

def test_oc_creation():
    m = MesaPROTON_OC()
    m.initial_agents = 500
    m.create_agents()
    m.number_weddings_mean = 1000
    for i in range(1, 5):
        m.wedding()
    # todo: fix this routine
    # m.setup_oc_groups()
    # print(m.total_num_links())

def test_big_crimes_for_small_fish():
    m = MesaPROTON_OC()
    m.initial_agents = 500
    m.max_accomplice_radius = 6
    m.create_agents()
    m.num_co_offenders_dist = [[5, 0.5], [6, 0.5], [10, 0.5]]
    for tick in range(1, 20):
        m.step()
    # todo: fix this routine
    # assert m.big_crime_from_small_fish < 0

def test_oc_crime_net_init():
    m = MesaPROTON_OC()
    m.create_agents()
    pass


def test_population_generator():
    m = MesaPROTON_OC()
    m.initial_agents = 2000
    m.load_stats_tables()
    m.facilitator_fails = 0
    m.facilitator_crimes = 0
    m.setup_persons_and_friendship()
    pass

def test_criminal_propensity_setup():
    m = MesaPROTON_OC()
    m.setup(1000)
    for line in m.c_range_by_age_and_sex:
        # the line variable is composed as follows:
        # [[bool(gender_is_male), int(minimum age range)], [int(maximum age range), float(c value)]]
        subpop = [agent for agent in m.schedule.agents if
                  agent.age() >= line[0][1] and agent.age() <= line[1][0] and agent.gender_is_male == line[0][0]]
        if subpop:
            total_c = 0
            for agent in subpop:
                total_c += agent.criminal_tendency
            assert ((total_c - len(subpop) * line[1][1]) / total_c < 1.0E-10)
