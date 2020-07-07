# that's strange - at somepoint it always failed the first run after changing something, then no more
import pytest
from mesaPROTON_OC import MesaPROTON_OC
import Person as pp


def test_random():
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

def test_weddings():
    m = MesaPROTON_OC()
    m.create_agents()
    print(len(m.schedule.agents) - len(pp.Person.persons))
    print(m.number_weddings)
    m.number_weddings_mean = 1000
    for i in range(1, 5):
        m.wedding()
    # print(Person.NumberOfLinks()-l)
    assert len([x for x in m.schedule.agents if x.partner and x.partner.partner != x]) == 0
    assert m.number_weddings == len([x for x in m.schedule.agents if x.partner]) / 2
    assert m.number_weddings > 0
    # coherent state of weddings

def test_inflate_deflate_network():
    m = MesaPROTON_OC(seed=10)
    m.create_agents()
    tot_links = m.total_num_links()
    assert tot_links

def test_generate_households():
    #For now we only check for errors
    m = MesaPROTON_OC(seed=42)
    m.initial_agents = 1000
    m.create_agents()
    m.generate_households()

def test_oc_creation():
    m = MesaPROTON_OC()
    m.initial_agents = 500
    m.create_agents()
    m.number_weddings_mean = 1000
    for i in range(1, 5):
        m.wedding()
    m.setup_oc_groups()
    print(m.total_num_links())

def test_big_crimes_for_small_fish():
    m = MesaPROTON_OC()
    m.initial_agents = 500
    m.max_accomplice_radius = 6
    m.create_agents()
    m.num_co_offenders_dist = [[5, 0.5], [6, 0.5], [10, 0.5]]
    for tick in range(1, 20):
        m.step()
    assert m.big_crime_from_small_fish < 0

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