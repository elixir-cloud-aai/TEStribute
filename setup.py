from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

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
