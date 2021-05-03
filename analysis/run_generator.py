import numpy as np
import pandas as pd
import json
import os

SAVE_PATH = "E:\\proton" #Your path here
PATH = "E:\\proton\\panel_abm_all.csv" #Your path here


data = pd.read_csv(PATH)

map = {"intervention":"intervention",
       "num-oc-persons": "num_oc_persons",
       "num-oc-families": "num_oc_families",
       "number-crimes-yearly-per10k": "number_crimes_yearly_per10k",
       "unemployment-multiplier": "unemployment_multiplier",
       "education-rate" : "education_modifier",
       "number-arrests-per-year":  "number_arrests_per_year",
       "punishment-length" : "punishment_length",
       "num-persons" : "initial_agents",
       "intervention-start" : "intervention_start",
       "intervention-end": "intervention_end",
       "nat-propensity-threshold": "nat_propensity_threshold",
       "oc-embeddedness-radius": "oc_embeddedness_radius",
       "threshold-use-facilitators" : "threshold_use_facilitators",
       "percentage-of-facilitators": "likelihood_of_facilitators",
       "nat-propensity-sigma" : "nat_propensity_sigma",
       "targets-addressed-percent" : "targets_addressed_percent",
       "nat-propensity-m" : "nat_propensity_m",
       "max-accomplice-radius" : "max_accomplice_radius",
       "ticks-between-intervention" : "ticks_between_intervention",
       "retirement-age" : "retirement_age",
       "OC-boss-repression?" : "oc_boss_repression",
       "constant-population?" : "constant_population",
       "migration-on?" : "migration_on",
       "facilitator-repression?" : "facilitator_repression",
       "facilitator-repression-multiplier" : "facilitator_repression_multiplier"}

num_ticks = 360

rp = dict()
for index, run in enumerate(data.groupby('run_id')):
    rp[index] = dict()
    for col in run[1].columns:
        if col in map.keys():
            rp[index][map[col]] = run[1][col].iloc[0]
            rp[index]["num_ticks"] = 360

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return super(NpEncoder, self).default(obj)

# with open(os.path.join(SAVE_PATH, "rp_comparison_can_weigh.json"), "w") as file:
#     json.dump(rp, file, cls=NpEncoder)
#
#
# """
# Only baseline:
# """
#
# new_rp = dict()
# for index, run in enumerate(rp.keys()):
#     if rp[run]["intervention"] == "baseline":
#         new_rp[index] = rp[run]
#
#
# with open(os.path.join(SAVE_PATH, "rp_comparison_can_weigh.json"), "w") as file:
#     json.dump(new_rp, file, cls=NpEncoder)