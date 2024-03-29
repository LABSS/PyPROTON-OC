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

from __future__ import annotations
from typing import Union, Dict, List
from protonoc.simulator.model import ProtonOC
from protonoc.simulator.model import extra
import os
from xml.dom import minidom
import json
import click
import sys
from concurrent.futures import ProcessPoolExecutor as Executor
from concurrent.futures import as_completed
import psutil
import time
import multiprocessing


class BaseMode:
    """
    Abstract class for Base mode
    """
    def __init__(self,
                 name: Union[str, None],
                 save_path: Union[str, bool],
                 snapshot: Union[str, None],
                 alldata: bool,
                 randomstate: int):

        self.save_path: str = save_path
        self.alldata: bool = alldata
        self.name: str = name
        self.snapshot_active = snapshot
        self.randomstate = randomstate
        print("Saving the data in: {}".format(self.save_path))
        self.args = list()

    def run(self) -> None:
        """
        Simple run function
        :return: None
        """
        self.args.append({"seed": self.randomstate,
                          "source_override": None,
                          "save_path": self.save_path,
                          "filename": self.name,
                          "verbose": True,
                          "snapshot": self.snapshot_active,
                          "alldata": self.alldata})
        self._single_run(self.args[0])
        click.echo(click.style("Done!", fg="red"))

    def _single_run(self, args: Dict) -> None:
        """
        This instantiates a model, performs a parameter override (if necessary),
        runs a simulation, and saves the data.
        :param args: List [seed, source_override, save_path, filename, verbose, snapshot, alldata]
        :return: None
        """
        if args["seed"] is None:
            args["seed"] = int.from_bytes(os.urandom(4), sys.byteorder)
        model = ProtonOC(seed=args["seed"], collect_agents=args["alldata"])
        if args["source_override"] is not None:
            model.override_dict(args["source_override"])
        model.run(verbose=args["verbose"])
        return model.save_data(save_dir=args["save_path"],
                        name=args["filename"],
                        snapshot=args["snapshot"])


class OverrideMode(BaseMode):
    """
    OverrideMode class
    """
    def __init__(self,
                 source_path: str,
                 save_path: Union[str, bool],
                 snapshot: Union[str, None],
                 alldata: bool,
                 randomstate: int,
                 parallel: bool,
                 merge=bool):
        super().__init__(name=None,
                         save_path=save_path,
                         snapshot=snapshot,
                         alldata=alldata,
                         randomstate=randomstate)

        self.source_path = source_path
        self.parallel = parallel
        self.merge = merge
        self.args = [run for subrun in self.detect_files() for run in subrun]

    def detect_files(self):
        """
        This method finds files to override model parameters, accepted extensions are json or xml.
        """
        all_plans = list()
        if os.path.isfile(self.source_path):
            if self.source_path.endswith(".json") or self.source_path.endswith(".xml"):
                if self.source_path.endswith(".json"):
                    all_plans.append(self.get_from_json(self.source_path))
                else:
                    all_plans.append(self.get_from_xml(self.source_path))
            else:
                raise Exception(self.source_path + " is not a valid file. "
                                                "\n Source file should be .json or .xml")
        else:
            for filename in os.scandir(self.source_path):
                if filename.path.endswith(".xml"):
                    all_plans.append(self.get_from_xml(filename.path))
                elif filename.path.endswith(".json"):
                    all_plans.append(self.get_from_json(filename.path))
                else:
                    pass
        return all_plans

    def get_from_xml(self, xml_file: str) -> List[Dict]:
        """
        This function override model parameters based on xml file and return a list with
        detected files.
        :param xml_file: str, xml path
        :return: List[Dict]
        """
        results = list()
        run = dict()
        name = os.path.basename(xml_file).replace(".xml", "")
        map_attr = {"education_rate": "education_modifier",
                    "data_folder": "city",
                    "[num_oc_persons]": "num_oc_persons",
                    "num_persons": "initial_agents",
                    "percentage_of_facilitators": "likelihood_of_facilitators"}
        mydoc = minidom.parse(xml_file)
        parameters = mydoc.getElementsByTagName('enumeratedValueSet')
        ticks = mydoc.getElementsByTagName('timeLimit')[0].attributes['steps'].value
        run["num_ticks"] = extra.standardize_value(ticks)
        for par in parameters:
            attribute = par.attributes['variable'].value.replace("-", "_").replace("?", "").lower()
            if attribute == "output" or attribute == "oc_members_scrutinize":
                continue
            if attribute in map_attr:
                attribute = map_attr[attribute]
            value = par.getElementsByTagName("value")[0].attributes["value"].value
            run[attribute] = extra.standardize_value(value)
        for rep in range(
                int(minidom.parse(xml_file).getElementsByTagName('experiment')[0].attributes[
                        'repetitions'].value)):
            results.append({"seed": self.randomstate,
                            "source_override": run,
                            "save_path": self.save_path,
                            "filename": name + "_run" + str(rep + 1),
                            "verbose": False if self.parallel else True,
                            "snapshot": self.snapshot_active,
                            "alldata": self.alldata})
        return results

    def get_from_json(self, source: str) -> List[Dict]:
        """
        This function override model parameters based on json file and return a list with
        detected files.
        :param source: str, json path
        :return: List[Dict]
        """
        extracted = list()
        with open(source, "rb") as file:
            js_file = json.load(file)
            name = os.path.basename(source).replace(".json", "")
            if type(js_file[list(js_file.keys())[0]]) == dict:
                for key in js_file.keys():
                    extracted.append({"seed": self.randomstate,
                                      "source_override": js_file[key],
                                      "save_path": self.save_path,
                                      "filename": name + str(key),
                                      "verbose": False if self.parallel else True,
                                      "snapshot": self.snapshot_active,
                                      "alldata": self.alldata})
            else:
                extracted.append({"seed": self.randomstate,
                                  "source_override": js_file,
                                  "save_path": self.save_path,
                                  "filename": name,
                                  "verbose": False if self.parallel else True,
                                  "snapshot": self.snapshot_active,
                                  "alldata": self.alldata})
        return extracted

    def run(self) -> None:
        """
        Simple run function
        :return: None
        """
        if self.parallel is not None:
            self._run_parallel()
        else:
            for arg in self.args:
                self._single_run(arg)
        if self.merge:
            self.merge_multiple_run()
        print("Done!")

    def _run_parallel(self) -> None:
        """
        This method performs numerous simulations in parallel.
        todo: Control memory growth.
        """
        if self.parallel > multiprocessing.cpu_count():
            self.parallel = multiprocessing.cpu_count()
        with Executor(max_workers=self.parallel) as executor:
            for out in as_completed([executor.submit(self._single_run, args) for args in
                                     self.args]):
                print(out.result())
                del out


    def merge_multiple_run(self) -> None:
        """
        Every simulation launched generates a single file, this function combines the generated
        files checking that the operation does not result in an Out of Memory.
        """
        to_merge = [file.path for file in os.scandir(self.save_path) if file.path.endswith(".pkl")]
        import pickle
        save_name = os.path.join(self.save_path,
                                 "proton_oc_{}_{}".format(str(time.localtime().tm_hour),
                                               str(time.localtime().tm_min)), + ".pkl")

        if sum([os.path.getsize(i) for i in to_merge]) > psutil.virtual_memory().free:
            raise MemoryError("Unable to merge, not enought memory")
        else:
            all_data = list()
            for i in to_merge:
                with open(i, "rb") as file:
                    data = pickle.load(file)
                    all_data.append(data)
                os.remove(i)
            with open(save_name, "wb") as file:
                pickle.dump(all_data, file)

if __name__ == "__main__":
    pass

