from setuptools import setup

setup(name='pyNAMEplot',
      version='0.1.4',
      description='Plots output of the NAME model',
      long_description=open("README.md").read(),
      url='https://github.com/TeriForey/pyNAMEplot',
      author='Teri Forey',
      author_email='trf5@le.ac.uk',
      license='LICENSE.txt',
      include_package_data=True,
      packages=[
            'pynameplot',
            'pynameplot.namereader',
      ],
      scripts=[
            'bin/makemastergrid.py',
            'bin/reproject.py',
            'bin/zonecsv.py',
            'bin/plotter.py'
      ],
      )
