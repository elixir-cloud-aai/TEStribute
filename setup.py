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
    author="ELIXIR Cloud & AAI",
    author_email="alexander.kanitz@alumni.ethz.ch",
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
    description="Task distribution for GA4GH TES instances",
    download_url="https://pypi.org/project/testribute",
    entry_points=[],
    install_requires=install_requires,
    keywords=(
        'ga4gh tes elixir rest api app openapi python task distribution'
    ),
    license="Apache License 2.0",
    license_file="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Alexander Kanitz",
    maintainer_email="alexander.kanitz@alumnni.ethz.ch",
    name="testribute",
    obsoletes=[],
    packages=find_packages(),
    platforms=[],
    project_urls={
        "Repository": "https://github.com/elixir-europe/TEStribute",
        "ELIXIR Cloud & AAI": "https://elixir-europe.github.io/cloud/",
        "Tracker": "https://github.com/elixir-europe/TEStribute/issues",
    },
    provides=[],
    python_requires='>=3.6',
    requires=[],
    setup_requires=[],
    url="https://github.com/elixir-europe/TEStribute",
    version="0.2.0",
)
