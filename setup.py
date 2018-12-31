import setuptools

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import sys

import adtrees


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="adtrees",
    version="0.0.1",
    author="Wojciech Widel",
    author_email="wwidel@irisa.fr",
    description="Implementation of attack(-defense) trees.",
    long_description=long_description,
    long_description_content_type="markdown",
    url="https://github.com/wwidel/adtrees/",
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    test_suite='adtrees.test.test_adtrees',
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5.5",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    extras_require={
        'testing': ['pytest']}
)
