#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:05:04 2020

@author: paolucci
"""
import Person
import numpy as np
import numba

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

def wedding_proximity_with(ego, pool):
    """
    Given an agent and a pool of agents this function returns a list of proximities with ego. Careful not to shuffle it!
    :param ego: Person
    :param pool: list of Person objects
    :return: list, list of proximities with ego.
    """
    proximity = np.array([(social_proximity(ego,x) + (4 - abs(x.hobby - ego.hobby)) / 4 ) / 2 for x in pool])
    if all([True for n in proximity if n <= 0]):
        proximity = np.ones(len(proximity))
    proximity /= np.sum(proximity)
    return proximity

def social_proximity(ego:Person, alter:Person):
    """
    This function calculates the social proximity between two agents based on age, gender, wealth level, education level and friendship
    :param ego: Person
    :param alter: Person
    :return: int, social proximity
    """
    acc = 0
    #normalization =  0
    acc += 1 - abs(alter.age() - ego.age()) / 18 if abs(alter.age() - ego.age()) < 18 else 0
    acc += 1 if alter.gender_is_male == ego.gender_is_male else 0
    acc += 1 if alter.wealth_level == ego.wealth_level else 0
    acc += 1 if alter.education_level == ego.education_level else 0
    acc += 1 if [x for x in alter.neighbors.get("friendship") if (x in ego.neighbors.get("friendship"))] else 0
    return acc

def at_most(agentset, n, rng_istance):
    if len(agentset) < n:
        return agentset
    else:
        return list(rng_istance.choice(agentset, n, replace=False))

def weighted_n_of(n, agentset, weight_function, rng_istance):
    p = [float(weight_function(x)) for x in agentset]
    for pi in p:
        if pi < 0:
            min_value = np.min(p)
            p = [i - min_value for i in p]
            break
    sump = sum(p)
    #if there are more zeros than n required in p
    if np.count_nonzero(p) < n:
        n = np.count_nonzero(p)
    #If there are only zeros
    if sump == 0:
        p = None
    else:
        p = [i/sump for i in p]
    #If the type is wrong
    if type(agentset) != list:
        agentset = list(agentset)
    return rng_istance.choice(agentset, int(n), replace=False, p=p)

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

#Numba functions
@numba.jit(nopython=True)
def _age(tick, birth_tick):
    return np.floor((tick - birth_tick) / 12)



