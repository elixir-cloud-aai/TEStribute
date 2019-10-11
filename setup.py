import os
from setuptools import setup, find_packages

# Read long description from file
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read requirements from file
install_requires = []
root_dir = os.path.dirname(os.path.realpath(__file__))
req = root_dir + '/requirements.txt'
if os.path.isfile(req):
    with open(req) as f:
        install_requires = f.read().splitlines()

setup(
    name="testribute",
    version="0.2.0",
    author="ElIXIR Cloud & AAI",
    author_email="alexander.kanitz@alumni.ethz.ch",
    description="Task distribution for GA4GH TES instances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    url="https://github.com/elixir-europe/TEStribute",
    install_requires=install_requires,
    python_requires='>=3.5',
    packages=find_packages(),
    keywords=(
        'ga4gh tes elixir rest api app openapi python'
        'task distribution'
    ),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
