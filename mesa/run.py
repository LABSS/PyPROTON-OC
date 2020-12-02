from model import ProtonOC
import os
import time
import sys
sys.setrecursionlimit(10000)

base_dir = "D:\\"
save_dir = os.path.join(base_dir, time.strftime("%d%m_%H%M"))
os.makedirs(save_dir)

def single_run(cls, dir, nrun):
    model = cls()
    model.intervention = "baseline"

    """
    Override
    """

    model.run(1000, 600, verbose=True)
    model.datacollector.get_agent_vars_dataframe().to_pickle(os.path.join(dir, str(nrun) + "agents" + ".pkl"))
    model.datacollector.get_model_vars_dataframe().to_pickle(os.path.join(dir, str(nrun) + "model" + ".pkl"))

for a in range(20):
    single_run(ProtonOC, save_dir, a)


if __name__ == "__main__":
    pass