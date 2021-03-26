# PROTON-OC

PROTON-OC is an agent-based model that explores the dynamics and processes that lead to recruitment into organized crime. The simulator investigates a wide variety of factors in the individual sphere and focuses on the social relationships between agents. Detailed information on the theoretical background, model development process, and model functioning available [here](./D5.1-PROTON-Simulator-Report.pdf). This is the python version of the simulator; the original model was developed in Netlogo and can be found [here](https://github.com/LABSS/PROTON-OC).

The simulation is developed by LABSS-CNR as a follow-up of the PROTON project, https://www.projectproton.eu/

Results from the original simulator have been published on the [Journal of Quantitative Criminology](https://link.springer.com/article/10.1007/s10940-020-09489-z).

## Get started

proton-oc requires python  >= 3.8, we recommend to use a virtual environment

```
pip install protonoc
```

### Command Line Interface

proton-oc integrates a **command line interface** that offers two usage modes:

1. base mode

   ```
   >> protonoc base --help
   Usage: protonoc base [OPTIONS]
   
     Run a simple baseline simulation
   
   Options:
     -name, -n TEXT            The name of the file being generated. By default
                               it is hour_minutes
   
     -collect, -c PATH         Specify the path where the results are saved.
                               (e.g. -c /this_folder/another_folder). default is
                               cwd
   
     -snapshot, -s INTEGER     If this option is passed with an integer value,
                               collects results only at certain ticks (e.g. -s 56
                               -s 89) save results at tick 56 and tick 89.
                               Accepts multiple calls, default is None.
   
     -alldata, -a              By default only model ouputs are collected. If
                               this option is passed the attributes of every
                               single agent are also collected. Warning: The
                               output may be large.
   
     -randomstate, -r INTEGER  If this option is called with an integer value,
                               the simulation uses that seed for the random
                               generator.
   
     --help                    Show this message and exit.
   ```

   Example:

   ```
   protonoc base -c result/ -n sample -r 42
   ```

   This command launches a simulation with baseline parameters, saves results in `result/` with the name `"sample"` and uses the seed `42`. Results are saved in pickle format.

2. override mode

   ```
   >> protonoc override --help
   Usage: protonoc override [OPTIONS] [SOURCE_PATH]
   
     This command takes as argument an .xml file a .json file or a folder
     containing several .json or .xml files. It overwrites the model parameters
     with the files and performs several simulations.
   
     SOURCE_PATH: file location, default is cwd
   
   Options:
     -collect, -c PATH         Specify the path where the results are saved.
                               (e.g. -c /this_folder/another_folder). default is
                               cwd
   
     -snapshot, -s INTEGER     If this option is passed with an integer value,
                               collects results only at certain ticks (e.g. -s 56
                               -s 89) save results at tick 56 and tick 89.
                               Accepts multiple calls, default is None.
   
     -alldata, -a              By default only model ouputs are collected. If
                               this option is passed the attributes of every
                               single agent are also collected. Warning: The
                               output may be large.
   
     -randomstate, -r INTEGER  If this option is called with an integer value,
                               the simulation uses that seed for the random
                               generator.
   
     -parallel, -p INTEGER     Adding this option with an int argument launches
                               multiple simulations in parallel using
                               concurrent.futures. The int value indicates how
                               many cores to use. If the value is too high adjust
                               the parameter based on the available machine's
                               cores. Be careful, it does not control memory
                               increase which may cause an out-of-memory.
   
     -merge, -m                Each simulation generates a single pickle file. If
                               this option is passed generates a single file
                               instead. Raise MemoryError if not enough memory
                               space.
   
     --help                    Show this message and exit.
   ```

Example:

```
protonoc override sample_json.json -c results/ -p 4 -m -a
```

This command takes the file `sample_json.json` (located in the samples folder) runs several simulations divided into 4 processes and saves the results in the `results/` folder. At the end of the simulation it merges all the results into one pickle file.

### Read data

Simulations results are saved in pickle and can be extracted as a pandas DataFrame through the `protonoc.utils` module.

```python
from protonoc import utils
path = "FILEPATH"
data = utils.read_data(path)
```

### Integrate the model in your scripts

Import `ProtonOC` as a simple module, create a new instance of the model and call the `run` function:

```python
from protonoc import ProtonOC
model = ProtonOC()
model.run(n_agents=100, num_ticks=480, verbose=True)
```

#### How do I change input parameters?

Import `ProtonOC` as a simple module, create a new instance of the model, use `ProtonOC.overview()` to show a pretty table with current parameters and the respective value. Use `ProtonOC.set_param()` to change the parameters of the active `ProtonOC` instance. Call the run function to launch the model.

```python
from protonoc import ProtonOC
model = ProtonOC()
model.overview()
model.set_param("initial_agents", 10000)
model.run(verbose=True)
```

sample `ProtonOC.overview()` output:

```
+-----------------------------------+----------+
|        free parameter name        |  value   |
+-----------------------------------+----------+
|            migration_on           |   True   |
|           initial_agents          |   10000  |
|             num_ticks             |   480    |
|            intervention           | baseline |
|       ......................      |    .     |
|       ......................      |    .     |
|       ......................      |    .     |
|       ......................      |    .     |
+-----------------------------------+----------+
```



## Contribute

Pyproton-oc accepts contributions. Reports and suggestions are welcome. Feedbacks are mandatory.
