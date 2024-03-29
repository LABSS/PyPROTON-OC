from setuptools import setup, find_packages

requires = ["click>=7.1.2",
            "networkx>=2.5",
            "numpy>=1.20",
            "pandas>=1.1.4",
            "tornado>=6.1",
            "tqdm>=4.53",
            "numba>=0.51.2",
            "psutil>=5.8.0",
            "mesa>=0.8.8",
            "prettytable>=2.1"]

extras_require = {
    "dev": ["pytest >= 4.6", "sphinx"],
    "docs": ["sphinx", "ipython"],
}

description = " Simulation of recruitment to terrorism. Developed by LABSS-CNR for the PROTON project, https://www.projectproton.eu"

with open('README.md') as file:
    readme = file.read()

setup(
   name='protonoc',
   version='1.0',
   description=description,
   long_description_content_type="text/markdown",
   long_description=readme,
   url="https://github.com/LABSS/PyPROTON-OC",
   author='LABSS(Francesco Mattioli, Mario Paolucci)',
   author_email='francesco@nientepanico.org, mario.paolucci@istc.cnr.it',
   package_dir={'protonoc': 'protonoc'},
   python_requires=">=3.8",
   package_data={
      "protonoc": [
         "simulator/inputs/general/data/*.csv",
         "simulator/inputs/palermo/data/*.csv",
         "simulator/inputs/eindhoven/data/*.csv",
      ]},
   packages=find_packages(),
   include_package_data=True,
   entry_points ={
      'console_scripts': ['protonoc=protonoc.main:mode'] },
   install_requires=requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Life",
        "Topic :: Sociology",
        "License :: OSI Approved :: MIT License"]
)