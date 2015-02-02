import os
import shutil
import sys
import glob
from setuptools import setup, find_packages


required_progs = [
    'blastn',
    'tblastn',
    'tblastx',
    'blastp',
    'blastx',
    'deltablast'
]

found_all_progs = True
print('Checking blast+ programs found in path:')
for program in required_progs:
    if shutil.which(program) is None:
        found_all_progs = False
        found = ' NOT FOUND'
    else:
        found = ' OK'
    print(found, program, sep='\t')

if not found_all_progs:
    print('Cannot install because some programs from the blast+ package not found.', file=sys.stderr)
    sys.exit(1)


setup(
    name='farm_blast',
    version='0.1.2',
    description='Package to run blast in parallel on a compute farm',
    packages = find_packages(),
    author='Martin Hunt',
    author_email='mh12@sanger.ac.uk',
    url='https://github.com/sanger-pathogens/Farm_blast',
    scripts=glob.glob('scripts/*'),
    test_suite='nose.collector',
    install_requires=['nose >= 1.3', 'pyfastaq >= 3.0.1', 'farmpy >= 0.2'],
    license='GPLv3',
)
