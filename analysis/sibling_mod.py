import pickle
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use("Tkagg")
import matplotlib.pyplot as plt
plt.style.use('ggplot')

map = {'count persons with [ migrant? ]' : "number_migrants",
       # "number-crimes" : "number_crimes",
       'sum [ num-crimes-committed ] of persons' : "number_crimes_committed_of_persons",
       'count persons' : "current_num_persons",
       'o1' : "current_oc_members",
       "o4" : "crimes_committed_by_oc_this_tick",
       "o5a" : "criminal_tendency_mean",
       "o12" : "number_law_interventions_this_tick",
       "o15" : "number_protected_recruited_this_tick",
       "o16" : "number_offspring_recruited_this_tick",
       "count prisoners" : "current_prisoners",
       'number-deceased' : "number_deceased",
       "number-born" : "number_born",
       'count persons with [ my-job != nobody ]' : "employed",
       'crime-size-fails' : "crime_size_fails",
       'count persons with [facilitator?]' : "facilitators",
       'facilitator-fails' : "facilitator_fails",
       'facilitator-crimes' : "facilitator_crimes",
       'people-jailed' : "people_jailed",
       'kids-intervention-counter' : "kids_intervention_counter",
       # 'count household-links' :"tot_household_link",
       'count partner-links' : "tot_partner_link",
       'count sibling-links' : "tot_sibling_link",
       'count offspring-links' : "tot_offspring_link",
       'count friendship-links' : "tot_friendship_link",
       'count criminal-links' : "tot_criminal_link",
       'count professional-links' : "tot_professional_link",
       'count school-links' : "tot_school_link",
       'sum [ count my-students ] of schools' : 'number_students',
       'count jobs' : "number_jobs",
       "[step]":"tick"}

PATH_PYTHON = "E:\\proton\\prox_more_siblings\\res" #YOUR PYTHON PATH HERE
PATH_NETLOGO = "E:\\proton\\comparative\\panel_abm_all.csv" #YOUR NETLOGO PATH HERE

interventions = ['baseline']
data_netlogo = dict()
data_python = dict()

for interv in pd.read_csv(PATH_NETLOGO).groupby("intervention"):
    data_netlogo[interv[0]] = interv[1]

all_data = list()
for index_run, run_file in enumerate(os.scandir(PATH_PYTHON)):
    out_data = pd.read_pickle(run_file.path)
    out_data["run_id"] = [index_run for n in range(361)]
    all_data.append(out_data)
total_python = pd.concat(all_data, ignore_index=True)

for interv in total_python.groupby("intervention"):
    data_python[interv[0]] = interv[1]

superrun_python = dict()
superrun_netlogo = dict()
for interv in interventions:
    reporter_python = data_python[interv][map.values()]
    superrun_python[interv] = pd.concat([tick.mean(axis=0) for number_tick, tick in
                                         reporter_python.groupby("tick")], axis=1).T

    reporter_netlogo = data_netlogo[interv][map.keys()]

    superrun_netlogo[interv] = pd.concat([tick.mean(axis=0) for number_tick, tick in
                                         reporter_netlogo.groupby(["[step]"])], axis=1).T

for interv in interventions:
    fig, axs = plt.subplots(2, 14, figsize=(180, 10))
    row = 0
    column = 0
    for metric_netlogo, metric_python in map.items():
        if column == 14:
            row = 1
            column = 0
        axs[row, column].plot(superrun_netlogo[interv][metric_netlogo], color="r",
                              label = "netlogo")
        axs[row, column].plot(superrun_python[interv][metric_python], color="b", label="python")
        axs[row, column].set_title(metric_netlogo + " // " + metric_python)
        axs[row, column].legend(loc='upper left', frameon=False)
        column += 1
    plt.savefig("mod_social_proxy_siblings.png")