from model import ProtonOC
from entities import Person
import numpy as np
import extra
import os
import sys
import pytest


if __name__ == "__main__":

    def generate_micro_net(model):
        for i in range(18):
            new_agent = Person(model)
            model.schedule.add(new_agent)
            new_agent.oc_member = False
            new_agent.facilitator = False
            new_agent.gender_is_male = i % 2 == 0
            new_agent.target_of_intervention = False
            new_agent.age = i * 149 % 45 + 10
            new_agent.education_level = i * 149 % 4
            new_agent.criminal_tendency = i * 149 % 100 / 100
            new_agent.wealth_level = i * 149 % 4
            new_agent.job_level = i * 149 % 4
            new_agent.propensity = i * 149 % 100 / 100
            new_agent.migrant = i % 3 == 0

        model.schedule.agents[0].make_partner_link(model.schedule.agents[1])
        model.schedule.agents[0].make_friendship_link(model.schedule.agents[2])
        model.schedule.agents[0].make_professional_link(model.schedule.agents[3])
        model.schedule.agents[0].make_school_link(model.schedule.agents[4])
        model.schedule.agents[0].add_criminal_link(model.schedule.agents[5])
        model.schedule.agents[0].num_co_offenses[model.schedule.agents[5]] = 5
        model.schedule.agents[5].num_co_offenses[model.schedule.agents[0]] = 5
        model.schedule.agents[5].make_parent_offsprings_link(model.schedule.agents[0])

        model.schedule.agents[6].make_friendship_link(model.schedule.agents[5])
        model.schedule.agents[7].make_partner_link(model.schedule.agents[8])
        model.schedule.agents[8].make_friendship_link(model.schedule.agents[9])
        model.schedule.agents[7].make_parent_offsprings_link(model.schedule.agents[9])
        model.schedule.agents[10].make_professional_link(model.schedule.agents[9])
        model.schedule.agents[10].make_professional_link(model.schedule.agents[11])
        model.schedule.agents[10].make_school_link(model.schedule.agents[13])

        model.schedule.agents[11].make_professional_link(model.schedule.agents[12])
        model.schedule.agents[12].make_professional_link(model.schedule.agents[13])
        model.schedule.agents[12].make_professional_link(model.schedule.agents[14])
        model.schedule.agents[12].make_professional_link(model.schedule.agents[16])

        model.schedule.agents[13].make_friendship_link(model.schedule.agents[15])
        model.schedule.agents[14].make_professional_link(model.schedule.agents[15])

        model.schedule.agents[14].make_household_link([model.schedule.agents[17]])
        model.schedule.agents[16].make_household_link([model.schedule.agents[12]])
        model.schedule.agents[16].make_household_link([model.schedule.agents[17]])

        model.schedule.agents[5].oc_member = True
        model.schedule.agents[17].oc_member = True
        model.schedule.agents[9].facilitator = True
        model.schedule.agents[3].facilitator = True

    model = ProtonOC()
    generate_micro_net(model)

    #test if the trouble starter if the last of the accomplices list
    assert model.schedule.agents[0].find_accomplices(5)[-1] == model.schedule.agents[0]
    assert model.schedule.agents[0].agents_in_radius(1)


    ag_9_range_3 = list()
    for i in [7,8,10,11,12,13,15]:
        ag_9_range_3.append(model.schedule.agents[i])
    ag_9_range_3 = set(ag_9_range_3)
    print(ag_9_range_3)

    ag_0_range_2 = list()
    for i in [1,2,3,4,5,6]:
        ag_0_range_2.append(model.schedule.agents[i])
    ag_0_range_2 = set(ag_0_range_2)
    print(ag_0_range_2)

    for i in range(1,6):
        print(model.schedule.agents[0].agents_in_radius(i))
        print(model.schedule.agents[9].agents_in_radius(i))
        print(model.schedule.agents[0].agents_in_radius(i)==ag_0_range_2)
        print(model.schedule.agents[9].agents_in_radius(i)==ag_9_range_3)

        print("kkkkkkkkkkkk")


