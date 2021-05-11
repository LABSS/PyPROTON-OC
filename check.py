import pandas as pd
import os
import numpy as np
new_path = "C:\\Users\\franc_pyl533c\OneDrive\Repository\PyPROTON-OC\protonoc\simulator\inputs\palermo\data"
old_path = "C:\\Users\\franc_pyl533c\OneDrive\Desktop\PROTON-OC-0.8\PROTON-OC-0.8\inputs\palermo\data"

all_new_names = [path.name for path in os.scandir(new_path)]

for path in os.scandir("C:\\Users\\franc_pyl533c\OneDrive\Desktop\PROTON-OC-0.8\PROTON-OC-0.8"
                       "\inputs\palermo\data"):
    if path.name in all_new_names and path.name != "work_status_by_edu_lvl.csv":
        new = pd.read_csv(os.path.join(new_path, path.name))
        old = pd.read_csv(path.path)
        print(path.name)
        print(all(old==new))
        print()

new_stuff = pd.read_csv(os.path.join(new_path,"work_status_by_edu_lvl.csv"))
old_stuff = pd.read_csv(os.path.join(old_path,"work_status_by_edu_lvl.csv"))

np.round(new_stuff.rate.to_numpy(dtype=float)) == np.round(old_stuff.rate.iloc[:32].to_numpy(
    dtype=float))
