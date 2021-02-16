from setuptools import setup, find_packages

requires = ["click", "networkx", "numpy", "pandas", "tornado", "tqdm", "numba"]

extras_require = {
    "dev": ["pytest >= 4.6", "sphinx"],
    "docs": ["sphinx", "ipython"],
}

setup(
   name='PyProton-OC',
   version='0.0.1',
   description='A useful module',
   author='LABSS(Francesco Mattioli, Mario Paolucci)',
   author_email='foomail@foo.com',
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
      'console_scripts': ['proton-oc=proton.main:mode'] },  #same as name
   install_requires=requires, #external packages as dependencies
)