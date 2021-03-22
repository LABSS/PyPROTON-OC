from setuptools import setup, find_packages

requires = ["click>=7.1.2",
            "networkx>=2.5",
            "numpy>=1.20",
            "pandas>=1.1.4",
            "tornado>=6.1",
            "tqdm>=4.53",
            "numba>=0.51.2",
            "psutil>=5.8.0",
            "mesa>=0.8.8"]

extras_require = {
    "dev": ["pytest >= 4.6", "sphinx"],
    "docs": ["sphinx", "ipython"],
}

description = " Simulation of recruitment to terrorism. Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu"

setup(
   name='pyproton-oc',
   version='0.1',
   description=description,
   author='LABSS(Francesco Mattioli, Mario Paolucci)',
   author_email='francesco@nientepanico.org, mario.paolucci@istc.cnr.it',
   package_dir={'proton': 'proton'},
   package_data={
      "proton": [
         "simulator/inputs/general/data/*.csv",
         "simulator/inputs/palermo/data/*.csv",
         "simulator/inputs/eindhoven/data/*.csv",
      ]},
   packages=find_packages(),
   include_package_data=True,
   entry_points ={
      'console_scripts': ['proton-oc=proton.main:mode'] },
   install_requires=requires,
)