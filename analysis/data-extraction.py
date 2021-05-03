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

PATH_PYTHON = "E:\\proton\\comparative\\res" #YOUR PYTHON PATH HERE
PATH_NETLOGO = "E:\\proton\\comparative\\panel_abm_all.csv" #YOUR NETLOGO PATH HERE

interventions = ['baseline', 'disruptive', 'facilitators', 'preventive', 'students']
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

#%%
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
    plt.savefig(interv + "_general.png")

#%%
for interv in interventions:
    fig, axs = plt.subplots(2, 14, figsize=(180, 10))
    row = 0
    column = 0
    for metric_netlogo, metric_python in map.items():
        if column == 14:
            row = 1
            column = 0
        axs[row, column].plot(superrun_netlogo[interv][metric_netlogo].rolling(
            window=36).mean(),
                              color="r",
                              label = "netlogo")
        axs[row, column].plot(superrun_python[interv][metric_python].rolling(
            window=36).mean(), color="b",
                              label="python")
        axs[row, column].set_title(metric_netlogo + " // " + metric_python)
        axs[row, column].legend(loc='upper left', frameon=False)
        column += 1
    plt.savefig(interv + "_rolling.png")

#%%
fig, axs = plt.subplots(2, 14, figsize=(180, 10))
row = 0
column = 0
for metric_netlogo, metric_python in map.items():
    if column == 14:
        row = 1
        column = 0
    for interv in interventions:
        axs[row, column].plot(superrun_netlogo[interv ][metric_netlogo].rolling(
            window=36).mean(),
                              label = "netlogo " + interv )
        axs[row, column].plot(superrun_python[interv][metric_python].rolling(
            window=36).mean(),
                              label="python" + interv)
        axs[row, column].set_title(metric_netlogo + " // " + metric_python)
        axs[row, column].legend(loc='upper left', frameon=False)
    column += 1
plt.savefig("all_interv_rolling.png")

#%%
for netlogo_label, python_label in map.items():
    row = 0
    column = 0
    fig, axs = plt.subplots(2, 3, figsize=(80, 10))
    for interv in interventions:
        if column == 3:
            row = 1
            column = 0

        axs[row, column].plot(superrun_python[interv][python_label],
                              label="python")

        axs[row, column].plot(superrun_netlogo[interv][netlogo_label],
                              label="netlogo")
        axs[row, column].axvline(x=13, label="intervention start")
        axs[row, column].axvline(x=36, label="intervention end")

        axs[row, column].set_title(interv)
        axs[row, column].legend(loc='upper left', frameon=False)

        column += 1

    plt.savefig("C:\\Users\\franc_pyl533c\\OneDrive\\Repository\\PyPROTON-OC\\analysis"
                "\\reporters_by_intervention_raw\\" + python_label + ".png")

#%%
for netlogo_label, python_label in map.items():
    row = 0
    column = 0
    fig, axs = plt.subplots(2, 3, figsize=(80, 10))
    for interv in interventions:
        if column == 3:
            row = 1
            column = 0

        axs[row, column].plot(superrun_python[interv][python_label].rolling(
            window=36).mean(),
                              label="python")

        axs[row, column].plot(superrun_netlogo[interv][netlogo_label].rolling(
            window=36).mean(),
                              label="netlogo")
        axs[row, column].axvline(x=13, label="intervention start")
        axs[row, column].axvline(x=36, label="intervention end")

        axs[row, column].set_title(interv)
        axs[row, column].legend(loc='upper left', frameon=False)

        column += 1

    plt.savefig("C:\\Users\\franc_pyl533c\\OneDrive\\Repository\\PyPROTON-OC\\analysis"
                "\\reporters_by_intervention_rolling\\" + python_label + ".png")


#%%
fig, axs = plt.subplots(1, 2)
for interv in interventions:
    axs[0].set_title("python")
    axs[0].plot(superrun_python[interv][map["o1"]], label=interv)
    axs[0].legend(loc='upper right', frameon=False)

    axs[1].set_title("netlogo")
    axs[1].plot(superrun_netlogo[interv]["o1"], label=interv)
    axs[1].legend(loc='upper right', frameon=False)


axs[0].axvline(x=13, label="intervention start")
axs[0].axvline(x=36, label="intervention end")
axs[1].axvline(x=13, label="intervention start")
axs[1].axvline(x=36, label="intervention end")
plt.show()