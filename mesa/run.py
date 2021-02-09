from typing import Union, List
import click
from model import ProtonOC
import os
from xml.dom import minidom
from collections import Counter
import multiprocessing
import time


class BaseMode:
    """
    Base mode class
    """
    def __init__(self, save_path: str, name: str):
        self.save_path: str = save_path
        self.name: str = name

    def run(self) -> None:
        """
        Simple run function
        :return: None
        """
        self._single_run(None, self.save_path, self.name)

    def _single_run(self, loc_xml: Union[str, None], save_dir: str, name: str, verbose=True) -> \
            None:
        """
        This instantiates a model, performs a parameter override (if necessary),
        runs a simulation, and saves the data.
        :param loc_xml: if it is a valid string it performs a parameter override from an xml file
        :param save_dir: directory where the results are saved
        :param name: run name
        :return: None
        """
        model = ProtonOC()
        model.override_xml(loc_xml)
        model.run(verbose=verbose)
        model.save_data(save_dir=save_dir, name=name)


class XmlMode(BaseMode):
    """
    Xml mode class
    """
    def __init__(self, xml_path: str, save_path: str, parallel: bool) -> None:
        super().__init__(save_path=save_path, name="None")
        self.files = list()
        self.parallel = parallel
        self.xml_path = xml_path
        self.detect_file()
        click.echo(click.style("Saving data in: " + self.save_path, bold=True, fg="red"))
        self.filenames = self.get_file_names(self.files)

    def detect_file(self):
        if os.path.isfile(self.xml_path):
            if self.xml_path[-3:] == "xml":
                runs = self.read_repetitions(self.xml_path)
                self.setup_repetitions(self.xml_path, runs)
            else:
                click.ClickException(
                    click.style(self.xml_path + " is not a valid xml file", fg="red"))
        else:
            for filename in os.scandir(self.xml_path):
                if filename.path.endswith('.xml'):
                    runs = self.read_repetitions(filename.path)
                    self.setup_repetitions(filename.path, runs)

    def setup_repetitions(self, path, runs):
        for repetition in range(runs):
            self.files.append(path)
        click.echo(click.style(str(runs) + " runs -> " + os.path.basename(
            path), fg="blue"))

    def run(self) -> None:
        """
        Performs multiple runs
        :return: None
        """
        cmd = click.prompt(click.style("\nConfirm [y/n]", fg="red", blink=True, bold=True),
                           type=str)
        if cmd == "y":
            if self.parallel:
                self.run_parallel()
            else:
                self.run_sequential()
        else:
            click.echo(click.style("\nAborted!", fg="red"))

    def read_repetitions(self, xml: str) -> int:
        """
        Given an xml file path extracts and returns the number of runs.
        :param xml: str, a valid xml file path
        :return: int, the number of runs
        """
        return int(minidom.parse(xml).getElementsByTagName('experiment')[0].attributes['repetitions'].value)

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
                names.append(os.path.basename(key)[:-4] + "_run_" + str(value + 1))
        return names

    def run_parallel(self) -> None:
        """
        Based on the self.files attribute runs multiple parallel simulations and saves the results.
        :return: None
        """
        processes = list()
        for file, name in zip(self.files, self.filenames):
            p = multiprocessing.Process(target=self._single_run, args=(file, self.save_path,
                                                                       name, False))
            processes.append(p)
            p.start()
        for process in processes:
            process.join()

    def run_sequential(self):
        """
        Based on the self.files attribute runs multiple sequential simulations and saves the
        results
        :return: None
        """
        for file, name in zip(self.files, self.filenames):
            self._single_run(file, self.save_path, name, True)


@click.group(help="PROTON-OC command line interface")
def mode():
    pass


@click.command(name="base", help=click.style("Runs a simulation with baseline parameters and "
                                             "saves results."))
@click.argument('save_path', type=click.Path(exists=True))
@click.option("--name", "--n", nargs=1, type=str, default="proton_oc_baseline_" + str(time.localtime().tm_hour) + "_" + str(
    time.localtime().tm_min))
def base_mode(save_path, name):
    mode = BaseMode(save_path, name)
    mode.run()


@click.command(name="xml", help=click.style("Performs multiple simulations based on one or more "
                                            "xml files and saves results."))
@click.argument('xml_path', type=click.Path(exists=True))
@click.argument('save_path', type=click.Path(exists=True))
@click.option("--p", "--parallel", is_flag=True)
def xml_mode(save_path, xml_path, p):
    mode = XmlMode(xml_path, save_path, p)
    mode.run()


@click.command(name="info")
def info():
    click.echo("Simulation of recruitment to terrorism \n"
               "Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu/")


mode.add_command(base_mode)
mode.add_command(xml_mode)
mode.add_command(info)

if __name__ == "__main__":
    mode()
