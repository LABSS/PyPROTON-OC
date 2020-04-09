#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:05:04 2020

@author: paolucci
"""
import Person


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
    l = [
        (social_proximity(ego,x) + 
         (4 - abs(x.hobby - ego.hobby)) / 4 ) / 2 for x in pool
        ]
    l /= l.sum()
    return l

def social_proximity(ego: Person, alter: Person):
    acc = 0
    #normalization =  0
    # age
    acc += 1 - abs(alter.age() - ego.age()) / 18 if abs(alter.age() - ego.age()) < 18 else 0
    acc += 1 if alter.gender == ego.gender else 0
    acc += 1 if alter.wealth_level == ego.wealth_level else 0
    acc += 1 if alter.education_level == ego.education_level else 0    
    acc += 1 if [x for x in alter.neighbors.get("friendship") if 
                 (x in ego.neighbors.get("friendship")) 
                 ] else 0
    return acc   