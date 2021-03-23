# PROTON-OC

Simulation of recruitment to terrorism

Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu/

## Get started:

proton-oc requires python  >= 3.8, we suggest to use a virtual environment for installation. 

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

   This command launches a simulation with baseline parameters, saves results in result/ with the name "sample" and uses the seed 42. Results are saved in pickle format.

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

This command takes the file sample_json.json (located in the samples folder) runs several simulations divided into 4 processes and saves the results in the results/ folder. At the end of the simulation it merges all the results into one pickle file.

### Read data:

To read generated data.

```python
from protonoc import utils
path = "FILEPATH"
data = utils.read_data(path)
```



### Integrate the model in your scripts

Import proton-oc as a simple library.

```python
from protonoc import ProtonOC
model = ProtonOC()
model.run(n_agents=100, num_ticks=480, verbose=True)
```

## Contribute

protonoc accepts contributions.