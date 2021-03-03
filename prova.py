import multiprocessing as mp
import numpy as np
from proton.simulator.model import ProtonOC

li = [str(x) for x in np.arange(15)]

def worke(name):
    model = ProtonOC()
    model.setup(1000)
    for a in range(100):
        model.step()
    model.save_data("D:\\proton\\json\\multiprova", name)
    return "Saved: " + name


if __name__ == "__main__":
    # procs = list()
    #     # instantiating process with arguments
    # for x in li:
    #     proc = mp.Process(target=worke, args=(x, ))
    #     procs.append(proc)
    #
    # # complete the processes
    # for proc in procs:
    #     proc.join()
    #
    # print("Done")
    processes = mp.cpu_count() - 2

    from multiprocessing import Pool
    with Pool(processes) as pool:
        pool.map(worke, li)

all = list()
import pickle
for b in li:
    with open('D:\\proton\\json\\multiprova\\' + b + ".pkl"  , 'rb') as f:
        file = pickle.load(f)
        all.append(file)

for x in all:
    for step in x[0].groupby("Step"):
        print(1)