from typing import Union, List
import click
import time
from run_modes import BaseMode, XmlMode, JsonMode

@click.group(help="PROTON-OC command line interface")
def mode():
    pass

@click.command(name="base",
               help=click.style("Runs a simulation with baseline parameters and saves results."))
@click.option("-collect",
              "-c",
              nargs=1,
              type=click.Path(exists=True), default=None)
@click.option("-name",
              "-n",
              nargs=1,
              type=str,
              default="proton_oc_baseline_{}_{}".format(str(time.localtime().tm_hour),
                                                        str(time.localtime().tm_min)))
@click.option("-snapshot",
              "-s",
              nargs=1,
              type=click.Path(exists=True),
              default=None)
def base_mode(name, collect, snapshot):
    mode = BaseMode(name, collect, snapshot)
    mode.run()


@click.command(name="xml", help=click.style("Performs multiple simulations based on one or more "
                                            "xml files and saves results."))
@click.argument('source_path', type=click.Path(exists=True))
@click.option("-collect",
              "-c",
              nargs=1,
              type=click.Path(exists=True), default=None)
@click.option("-snapshot",
              "-s",
              nargs=1,
              type=click.Path(exists=True),
              default=None)
@click.option("-parallel", "-p", is_flag=True)
def xml_mode(source_path, collect, parallel, snapshot):
    mode = XmlMode(source_path, collect, parallel, snapshot)
    mode.run()


@click.command(name="json", help=click.style("Performs multiple simulations based on one or more "
                                            "json files and saves results."))
@click.argument('source_path', type=click.Path(exists=True))
@click.option("-collect",
              "-c",
              nargs=1,
              type=click.Path(exists=True), default=None)
@click.option("-snapshot",
              "-s",
              nargs=1,
              type=click.Path(exists=True),
              default=None)
@click.option("-parallel", "-p", is_flag=True)
def json_mode(source_path, collect, parallel, snapshot):
    mode = JsonMode(source_path, collect, parallel, snapshot)
    mode.run()


@click.command(name="info")
def info():
    click.echo("Simulation of recruitment to terrorism \n"
               "Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu/")


mode.add_command(base_mode)
mode.add_command(xml_mode)
mode.add_command(json_mode)
mode.add_command(info)

if __name__ == "__main__":
    mode()
