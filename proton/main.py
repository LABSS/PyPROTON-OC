
# MIT License
#
# Copyright (c) 2019 LABSS(Francesco Mattioli, Mario Paolucci)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import click
import time
from proton.run_modes import BaseMode, OverrideMode
import os

@click.group(help="PROTON-OC command line interface")
def mode():
    pass

@click.command(name="base")
@click.option("-name",
              "-n",
              nargs=1,
              type=str,
              default="proton_oc_{}_{}".format(str(time.localtime().tm_hour),
                                               str(time.localtime().tm_min)),
              help="The name of the file being generated. By default it is hour_minutes")
@click.option("-collect",
              "-c",
              nargs=1,
              type=click.Path(exists=True),
              default=os.getcwd(),
              help="Specify the path where the results are saved. (e.g. -c "
                   "/this_folder/another_folder). default is cwd")
@click.option("-snapshot",
              "-s",
              type=int,
              default=False,
              multiple=True,
              help="If this option is passed with an integer value, collects results "
                   "only at certain ticks (e.g. -s 56 -s 89) save results at tick 56 and tick 89. "
                   "Accepts multiple calls, default is None.")

@click.option("-alldata",
              "-a",
              is_flag=True,
              default=False,
              help="By default only model ouputs are collected. If this option is passed "
                   "the attributes of every single agent are also collected. Warning: The output "
                   "may be large.")
@click.option("-randomstate",
              "-r",
              type=int,
              default=None,
              help="If this option is called with an integer value, the simulation uses "
                   "that seed for the random generator.")
@click.pass_context
def base_mode(*args,
              name,
              collect,
              snapshot,
              alldata,
              randomstate,
              **kwargs):
    """
    Run a simple baseline simulation
    """
    mode = BaseMode(name=name,
                    save_path=collect,
                    snapshot=snapshot,
                    alldata=alldata,
                    randomstate=randomstate)
    mode.run()


@click.command(name="override")
@click.argument('source_path', type=click.Path(exists=True), default=os.getcwd())
@click.option("-collect",
              "-c",
              nargs=1,
              type=click.Path(exists=True),
              default=os.getcwd(),
              help="Specify the path where the results are saved. (e.g. -c "
                   "/this_folder/another_folder). default is cwd")
@click.option("-snapshot",
              "-s",
              type=int,
              default=False,
              multiple=True,
              help="If this option is passed with an integer value, collects results "
                   "only at certain ticks (e.g. -s 56 -s 89) save results at tick 56 and tick 89. "
                   "Accepts multiple calls, default is None.")

@click.option("-alldata", "-a", 
              is_flag=True, 
              help="By default only model ouputs are collected. If this option is passed "
                   "the attributes of every single agent are also collected. Warning: The output "
                   "may be large.")
@click.option("-randomstate",
              "-r",
              type=int,
              default=None,
              help="If this option is called with an integer value, the simulation uses "
                   "that seed for the random generator.")
@click.option("-parallel",
              "-p",
                nargs=1,
              default=None,
              type=int,
              help="adding this option with an int argument launches multiple simulations in "
                   "parallel using concurrent.futures. The int argument specifies the number of "
                   "concurrent processes that are spawned.")
@click.option("-merge",
              "-m",
              is_flag=True,
              default=False,
              help="Each simulation generates a single pickle file with the results. If this option "
                   "is passed generates a single file instead. Raise MemoryError "
                   "if not enough memory space.")
@click.pass_context
def override(*args,
             source_path,collect,
             snapshot,
             alldata,
             randomstate,
             parallel,
             merge,
             **kwargs):
    """
    This command takes as argument an .xml file a .json file or a folder containing several .json or .xml files.
    It overwrites the model parameters with the files and performs several simulations.

    SOURCE_PATH: file location, default is cwd

    """
    mode = OverrideMode(source_path,
                        save_path=collect,
                        snapshot=snapshot,
                        alldata=alldata,
                        randomstate=randomstate,
                        parallel=parallel,
                        merge=merge)
    mode.run()

@click.command(name="info")
def info():
    click.echo("Simulation of recruitment to terrorism \n"
               "Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu/")

mode.add_command(base_mode)
mode.add_command(override)
mode.add_command(info)

if __name__ == '__main__':
    mode()