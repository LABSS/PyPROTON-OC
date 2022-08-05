#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  2 19:52:26 2021

@author: paolucci
"""

from protonoc import ProtonOC
model = ProtonOC()
model.run(n_agents=1000, num_ticks=480, verbose=True)