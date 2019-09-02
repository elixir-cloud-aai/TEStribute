import os
from setuptools import setup, find_packages

# Read long description from file
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read requirements from file
install_requires = []
# Alternatively, add only main requirements directly, *NOT* their
# dependencies.
# In any case it should be good to remove the GitHub installs and
# upload packages to PyPI
root_dir = os.path.dirname(os.path.realpath(__file__))
req = root_dir + '/requirements.txt'
if os.path.isfile(req):
    with open(req) as f:
        install_requires = f.read().splitlines()

setup(
    name="TEStribute",
    version="0.1.0",
    author="Elixir Europe",
    author_email="alexander.kanitz@alumni.ethz.ch",
    description="LB for TES endpoints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    url="https://github.com/elixir-europe/TEStribute",
    install_requires=install_requires,
    packages=find_packages(),
    keywords=(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)

