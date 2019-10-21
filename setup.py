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
    name="TEStribute",
    version="0.2.0",
    description="Task distribution for GA4GH TES instances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elixir-europe/TEStribute",
    author="ELIXIR Cloud & AAI",
    author_email="alexander.kanitz@alumni.ethz.ch",
    maintainer="Alexander Kanitz",
    maintainer_email="alexander.kanitz@alumnni.ethz.ch",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    entry_points={
        'console_scripts': [
            'testribute = TEStribute.cli:main',
        ],
    },
    keywords=(
        'ga4gh tes elixir rest api app openapi python task distribution'
    ),
    project_urls={
        "Repository": "https://github.com/elixir-europe/TEStribute",
        "ELIXIR Cloud & AAI": "https://elixir-europe.github.io/cloud/",
        "Tracker": "https://github.com/elixir-europe/TEStribute/issues",
    },
    packages=find_packages(),
    install_requires=install_requires,
    python_requires='~=3.6',
    include_package_data=True,
    setup_requires=[
        "setuptools_git == 1.2",
    ],
)
