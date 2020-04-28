#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 12:29:10 2020

@author: paolucci
"""

import unittest
from mesaPROTON_OC import MesaPROTON_OC
import Person as pp
import random

class TestPROTON(unittest.TestCase):

    # that's strange - at somepoint it always failed the first run after changing something, then no more
    def test_weddings(self):
        random.seed(the_seed)
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
        random.seed(the_seed)
        pp.persons = []
        # testing link exploration
        links = [[4,5],[2,3],[1],[1,8],[0,6,5,7],[4,0],[4],[4,8],[9,3,8],[8]]
        m = MesaPROTON_OC()
        for i in range(0,10): 
            pp.Person(m)
        for i in range(0,10):
            for l in links[i]: pp.Person.persons[i].neighbors.get('friendship').add(pp.Person.persons[l])
        # for i in range(0,10): 
        #     print([x.unique_id for x in pp.Person.persons[i].neighbors.get('friendship')])
        ne =  pp.Person.persons[5].neighbors_range('friendship', 3 )
        self.assertEqual(sorted([x.unique_id for x in ne]), [0, 4, 6, 7, 8])
        #print([x.unique_id for x in ne]) # should be [ 4, 7, 8, 0, 6]

if __name__ == '__main__':
    the_seed = random.randint(0,1000000)
    unittest.main()
    print("the seed is: " + str(the_seed))