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

from typing import Union, List
from .simulator.model import ProtonOC
import os
from xml.dom import minidom
from collections import Counter
import multiprocessing
import json
import click
import sys
from concurrent.futures import ProcessPoolExecutor as Executor

class BaseMode:
    """
    Base mode class
    """
    def __init__(self, name: Union[str, None], save_path: Union[str, bool],
                 snapshot: Union[str, None]):
        if snapshot is not None:
            self.save_path = snapshot
            self.snapshot_active = True
            self.collect = False
        else:   
            self.save_path: Union[str, bool] = save_path
            self.collect = True
            self.snapshot_active = False
        self.name: str = name

    def run(self) -> None:
        """
        Simple run function
        :return: None
        """

        self._single_run([None, None, self.save_path , self.name, True])
        click.echo(click.style("Done!", fg="red"))

    def _single_run(self, args: List) -> None:
        """
        This instantiates a model, performs a parameter override (if necessary),
        runs a simulation, and saves the data.
        :param args: List [seed, source_file, save_dir, name, verbose]
        :return: None
        """
        if args[0] is None:
            args[0] = int.from_bytes(os.urandom(4), sys.byteorder)
        model = ProtonOC(seed = args[0], collect=self.collect)
        if self.snapshot_active:
            model.init_snapshot_state(name=args[3], path=self.save_path)
        if args[1] is not None:
            model.override(args[1])
        model.run(verbose=args[4])
        if self.collect and args[2]:
            model.save_data(save_dir=args[2], name=args[3])


class XmlMode(BaseMode):
    """
    Xml mode class
    """
    def __init__(self,
                 source_path: str,
                 save_path: str,
                 parallel: bool,
                 snapshot: Union[str, bool],
                 filetype: str = ".xml") -> None:

        super().__init__(name=None, save_path=save_path, snapshot=snapshot)
        self.files = list()
        self.parallel = parallel
        self.source_path = source_path
        self.filetype = filetype
        self.detect_file(self.filetype)
        # click.echo(click.style("Saving data in: " + self.save_path, bold=True, fg="red"))
        self.filenames = self.get_file_names(self.files)

    def detect_file(self, filetype):
        if os.path.isfile(self.source_path):
            if os.path.splitext(self.source_path)[1] == filetype:
                runs = self.read_repetitions(self.source_path)
                self.setup_repetitions(self.source_path, runs)
            else:
                click.ClickException(
                    click.style("{} is not a valid {} file".format(self.source_path, filetype),
                                fg="red"))
        else:
            for filename in os.scandir(self.source_path):
                if filename.path.endswith(filetype):
                    runs = self.read_repetitions(filename.path)
                    self.setup_repetitions(filename.path, runs)

    def setup_repetitions(self, path, runs):
        for repetition in range(runs):
            self.files.append(path)
        # click.echo(click.style(str(runs) + " runs -> " + os.path.basename(
            # path), fg="blue"))

    def run(self) -> None:
        """
        Performs multiple runs
        :return: None
        """
        # cmd = click.prompt(click.style("\nConfirm [y/n]", fg="red", blink=True, bold=True),
        #                    type=str)
        cmd = "y"
        if cmd == "y":
            if self.parallel:
                self.run_parallel()
            else:
                self.run_sequential()
            click.echo(click.style("Done!", fg="red"))
        else:
            click.echo(click.style("\nAborted!", fg="red"))


    def read_repetitions(self, source: str) -> int:
        """
        Given an xml file path extracts and returns the number of runs.
        :param xml: str, a valid xml file path
        :return: int, the number of runs
        """
        return int(minidom.parse(source).getElementsByTagName('experiment')[0].attributes[
                       'repetitions'].value)

    def get_file_names(self, files: List[str]) -> List[str]:
        """
        Given a list of xml files extracts the filename and return a list.
        :param files: a list of valid xml file paths
        :return: List, a list of filenames
        """
        rep = Counter(files)
        names = list()
        for key in rep:
            for value in range(rep[key]):
                names.append(os.path.basename(key)[:-5] + "_run_" + str(value + 1))
        return names

    def run_parallel(self) -> None:
        """
        Based on the self.files attribute runs multiple parallel simulations and saves the results.
        :return: None
        """
        args = list()
        for file, name in zip(self.files, self.filenames):
            args.append([int.from_bytes(os.urandom(4), sys.byteorder),
                              file,
                              self.save_path,
                              name, False])

        MAX_CONCURRENCY = multiprocessing.cpu_count() - 2
        N_WORKERS = min(len(args), MAX_CONCURRENCY)
        with Executor(max_workers=N_WORKERS) as executor:
            futures = [executor.submit(self._single_run, arg) for arg in args]
            for future in futures:
                try:
                    result = future.result()
                except Exception as e:
                    print(e)



    def run_sequential(self):
        """
        Based on the self.files attribute runs multiple sequential simulations and saves the
        results
        :return: None
        """
        for file, name in zip(self.files, self.filenames):
            self._single_run([None, file, self.save_path, name, True])

class JsonMode(XmlMode):
    def __init__(self, source_path: str, save_path: str, 
                 parallel: bool, snapshot: Union[str, bool]) -> None:
        super().__init__(source_path=source_path, save_path=save_path, parallel=parallel,
                         filetype=".json", snapshot=snapshot)

    def read_repetitions(self, source: str) -> int:
        """
        Given an xml file path extracts and returns the number of runs.
        :param xml: str, a valid xml file path
        :return: int, the number of runs
        """
        with open(source) as json_file:
            data = json.load(json_file)
            if "repetitions" in data:
                return data["repetitions"]
            else:
                return 1


