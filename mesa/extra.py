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
    return  rng_istance.choice(agentset, int(n), replace=False, p=p)

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

#Data Collectors
#Agents Method
def get_n_household_links(agent):
    return list(agent.neighbors.get("household"))

def get_n_friendship_links(agent):
    return list(agent.neighbors.get("friendship"))

def get_n_criminal_links(agent):
    return list(agent.neighbors.get("criminal"))

def get_n_professional_links(agent):
    return list(agent.neighbors.get("professional"))

def get_n_school_links(agent):
    return list(agent.neighbors.get("school"))

def get_n_sibling_links(agent):
    return list(agent.neighbors.get("sibling"))

def get_n_offspring_links(agent):
    return list(agent.neighbors.get("offspring"))

def get_n_partner_links(agent):
    return list(agent.neighbors.get("partner"))

def get_criminal_tendency(agent):
    return agent.criminal_tendency

#Model Methods
def get_n_agents(model):
    return len(model.schedule.agents)

def o1(model):
    """
    Get number of current OC members
    :param model: model obj
    :return: int, number of current OC members
    """
    return len([agent for agent in model.schedule.agents if agent.oc_member])

def o2(model):
    """
    get the number of recruited individuals into OC per time unit
    :param model: model obj
    :return: int, number of recruited individuals into OC
    """
    return len([agent for agent in model.schedule.agents if agent.new_recruit == (model.ticks - 1)])

def o3(model):
    """
    Get the number of crimes per time unit
    :param model: model obj
    :return: int, the number of crimes
    """
    return np.sum([agent.num_crimes_committed_this_tick for agent in model.schedule.agents])

def o4(model):
    """
    get the number of crimes committed by OC members per time unit
    :param model: model obj
    :return: int, number of crimes committed by OC members
    """
    return np.sum(agent.num_crimes_committed_this_tick for agent in model.schedule.agents if agent.oc_member)

def o5(model):
    """
    Distribution of C (which is the individual propensity towards crime commission)
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o5a(model):
    """
    # get the average of C (which is the individual propensity towards crime commission)
    :param model: model obj
    :return:
    """
    return np.mean([agent.criminal_tendency for agent in model.schedule.agents])

def o6(model):
    """
    Distribution of R (which is the individual embededdness into OC-prone local networks)
    :param model: model obj
    :return:
    """
    # todo: create a visualization to add this graph
    pass

def o6a(model):
    """
    get average of R (which is the individual embededdness into OC-prone local networks)
    :param model: model obj
    :return: int, average of R
    """
    criminals = [agent for agent in model.schedule.agents if agent.oc_member]
    if criminals:
        return np.mean([crim.oc_embeddedness_fresh for crim in criminals])
    else:
        return 0

def o7a(model):
    """
    Draw the distribution of socio-demographic variables on new recruited individuals
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o7b(model):
    """
    draw the distribution of socio-demographic variables on new recruited individuals
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o7c(model):
    """
    draw the distribution of socio-demographic variables on new recruited individuals
    :param model:model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o8a(model):
    """
    draw the distribution of socio-demographic variables of OC members
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o8b(model):
    """
    draw the distribution of socio-demographic variables of OC members
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o8c(model):
    """
    draw the distribution of socio-demographic variables of OC members
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o9a(model):
    """
    draw the distribution of socio-demographic variables of “ordinary criminals” (people that commit crime but are not part of an OC)
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o9b(model):
    """
    draw the distribution of socio-demographic variables of “ordinary criminals” (people that commit crime but are not part of an OC)
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o9c(model):
    """
    draw the distribution of socio-demographic variables of “ordinary criminals” (people that commit crime but are not part of an OC)
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o10a(model):
    """
    darw the distribution of socio-demographic variables of the general population
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o10b(model):
    """
    darw the distribution of socio-demographic variables of the general population
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o10c(model):
    """
    darw the distribution of socio-demographic variables of the general population
    :param model: model obj
    :return: None
    """
    # todo: create a visualization to add this graph
    pass

def o11(model):
    """
    Get the number of crimes committed by facilitator agents per time unit
    :param model: model obj
    :return: int, number of crimes committed by facilitator agents
    """
    return np.sum([agent.num_crimes_committed_this_tick for agent in model.schedule.agents if agent.facilitator ])

def o12(model):
    """
    Get the number of law enforcement interventions per time unit
    :param model: model obj
    :return: int, number of law enforcement interventions
    """
    return model.number_law_interventions_this_tick

def o13(model):
    """
    Get the age structure of offenses, return a list with 8 elements that correspond to these bins:
    0-13, 13-17, 17-24, 24-34, 34-44, 44-54, 54-64, 64-200
    :param model: model obj
    :return: list, age structure of offenses
    """
    age_bins = [0, 13, 17, 24, 34, 44, 54, 64, 200]
    sum = list()
    for index,n in enumerate(age_bins):
        if index == len(age_bins) - 1:
            break
        else:
            sum.append(np.sum([agent.num_crimes_committed_this_tick for agent in model.schedule.agents if agent.age() > n and agent.age() <= age_bins[index+1]]))
    return sum

def o14(model):
    """
    get co-offenses per turn. A vector of co-offenses the side of the index, starting with zero.
    :param model: model obj
    :return: list
    """
    # todo: add the function make-co-offending-histo
    pass

def o15(model):
    """
    get the number of persons addressed by a preventive interventions recruited this tick
    :param model: model obj
    :return: int, number of persons addressed by a preventive interventions recruited
    """
    return model.number_protected_recruited_this_tick

def o16(model):
    """
    get the number of OC person offsprings recruited this tick
    :param model: model obj
    :return: int, number of OC person offsprings recruited
    """
    return model.number_offspring_recruited_this_tick


#Numba functions
@numba.jit(nopython=True)
def _age(tick, birth_tick):
    return np.floor((tick - birth_tick) / 12)



