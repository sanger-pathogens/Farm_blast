import os
import glob
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='Farm_blast',
    version='0.1',
    description='Package to run blast in parallel on a compute farm',
    long_description=read('README.md'),
    packages = find_packages(),
    author='Martin Hunt',
    author_email='mh12@sanger.ac.uk',
    url='https://github.com/sanger-pathogens/Farm_blast',
    scripts=glob.glob('scripts/*'),
    test_suite='nose.collector',
    install_requires=['nose >= 1.3', 'fastaq >= 0.1', 'farmpy >= 0.2'],
    license='GPLv3',
)
