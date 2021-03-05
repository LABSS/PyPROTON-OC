import numpy as np
import json
import itertools

params = {"intervention": ["facilitators","students", "disruptive", "preventive","baseline" ],
          "num_oc_persons": np.arange(20, 50, 4), # ->100
          "num_oc_families": np.arange(4, 34, 4),
          "number_arrests_per_year": np.arange(20, 50, 4)}

combinations = [comb for comb in itertools.product(params["intervention"],
                                                   params["num_oc_persons"],
                                                   params["num_oc_families"],
                                                   params["number_arrests_per_year"])]

print(len(combinations))