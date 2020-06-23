#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 12:29:10 2020

@author: paolucci
"""

import unittest
from mesaPROTON_OC import MesaPROTON_OC
import Person as pp
import extra

class TestPROTON(unittest.TestCase):

    # that's strange - at somepoint it always failed the first run after changing something, then no more
    def test_weddings(self):
        #random.seed(the_seed)
        m = MesaPROTON_OC()
        m.create_agents()
        print(len(m.schedule.agents)-len(pp.Person.persons))
        print(m.number_weddings)
        m.number_weddings_mean = 1000
        for i in range(1,5):
            m.wedding()
        #print(Person.NumberOfLinks()-l)
        self.assertEqual(len([x for x in m.schedule.agents if x.partner and x.partner.partner != x]), 0)
        self.assertEqual(m.number_weddings, len([x for x in m.schedule.agents if x.partner]) / 2)
        self.assertTrue(m.number_weddings > 0)
        # coherent state of weddings

    def test_networks(self):
        #random.seed(the_seed)
        pp.persons = []
        # testing link exploration
        links = [[4,5],[2,3],[1],[1,8],[0,6,5,7],[4,0],[4],[4,8],[9,3,8],[8]]
        m = MesaPROTON_OC()
        for i in range(0,10): 
            pp.Person(m)
        for i in range(0,10):
            for l in links[i]:
                pp.Person.persons[i].neighbors.get('friendship').add(pp.Person.persons[l])
        # for i in range(0,10): 
        #     print([x.unique_id for x in pp.Person.persons[i].neighbors.get('friendship')])
        ne =  pp.Person.persons[5].neighbors_range('friendship', 3 )
        self.assertEqual(sorted([x.unique_id for x in ne]), [0, 4, 6, 7, 8])
        #print([x.unique_id for x in ne]) # should be [ 4, 7, 8, 0, 6]
        
        
    def test_inflate_deflate_network(self):
        #random.seed(the_seed)
        m = MesaPROTON_OC()
        m.create_agents()
        print(m.total_num_links())
        
    def test_oc_creation(self):
        #random.seed(the_seed)
        m = MesaPROTON_OC()
        m.create_agents()
        m.setup_oc_groups()
        print(m.total_num_links())

    def test_big_crimes_for_small_fish(self):
        m = MesaPROTON_OC()
        m.initial_agents = 500
        m.max_accomplice_radius = 6
        m.create_agents()
        m.num_co_offenders_dist = [[5, 0.5], [6, 0.5], [10, 0.5]]
        for tick in range(1,20):
            m.step()
        self.assertTrue(m.big_crime_from_small_fish < 0, msg=None)

    def test_random(self):
        m = MesaPROTON_OC(seed=42)
        self.assertEqual(m.check_random, [0.7739560485559633, 0.6394267984578837])

    def test_oc_crime_net_init(self):
        m = MesaPROTON_OC()
        m.create_agents()
        pass

    def test_population_generator(self):
        m = MesaPROTON_OC()
        m.initial_agents = 2000
        m.load_stats_tables()
        m.facilitator_fails = 0
        m.facilitator_crimes = 0
        m.setup_persons_and_friendship()
        pass



if __name__ == '__main__':
    #the_seed = random.randint(0,1000000)
    unittest.main()
    #print("the seed is: " + str(the_seed))