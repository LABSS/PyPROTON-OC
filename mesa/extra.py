#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:05:04 2020

@author: paolucci
"""
import Person
import numpy as np

# basic graph methods could be copied from https://www.python-course.eu/graphs_python.php
def print_id(p):
    print([x.pid for x in p])
    
def find_neighb(netname, togo, found, border):
    # found and border must have null intersection
    # includes the initial found
    # https://stackoverflow.com/questions/12555627/python-3-starred-expression-to-unpack-a-list
    found = found | border
    if togo == 0: return found
    #print_id(set().union(*[x.neighbors.get(netname) for x in border]))
    nextlayer = set().union(*[x.neighbors.get(netname) for x in border]) - found
    if not nextlayer:
        return found
    else:
        togo -= 1
        return find_neighb(netname, togo, found, nextlayer)
    
# utility functions
def wedding_proximity_with(ego, pool): # returns a list of proximities with ego. Careful not to shuffle it!
    l = np.array([
        (social_proximity(ego,x) + 
         (4 - abs(x.hobby - ego.hobby)) / 4 ) / 2 for x in pool
        ])
    l /= l.sum()
    return l

def social_proximity(ego:Person, alter:Person):
    acc = 0
    #normalization =  0
    # age
    acc += 1 - abs(alter.age() - ego.age()) / 18 if abs(alter.age() - ego.age()) < 18 else 0
    acc += 1 if alter.gender_is_male == ego.gender_is_male else False
    acc += 1 if alter.wealth_level == ego.wealth_level else 0
    acc += 1 if alter.education_level == ego.education_level else 0    
    acc += 1 if [x for x in alter.neighbors.get("friendship") if 
                 (x in ego.neighbors.get("friendship")) 
                 ] else 0
    return acc

def at_most(n, a, rng_istance, replace=True):
    return a if len(a) < n else rng_istance.choice(a,n,replace=replace)


def weighted_n_of(n, agentset, weight_function, rng_istance):
    # todo: check for positives
    p = [float(weight_function(x)) for x in agentset]
    sump = sum(p)
    #minp = min(p)
    #maxp = max(p)
    p = [i/sump for i in p]
    return  rng_istance.choice(agentset, n, replace=False, p=p)

def weighted_one_of(agentset, weight_function, rng_istance):
    return weighted_n_of(1, agentset, weight_function, rng_istance)[0]

def pick_from_pair_list(a_list_of_pairs, rng_istance):
    """
    given a list of pairs, containing an object and a probability (e.g. [[object, p],[object, p]])
    return an object based on the probability(p)
    :param a_list_of_pairs:list, a list of pairs (e.g. [[object, p],[object, p]])
    :param rng_istance: numpy.random instance,
    :return: object
    """
    return weighted_one_of(a_list_of_pairs, lambda x: x[-1], rng_istance)[0]