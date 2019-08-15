# TEStribute

Task distribution for GA4GH TES services.

## Synopsis

Proof of concept implementation of a task distribution logic for a federated
network of GA4GH TES services. Given lists of available GA4GH TES and DRS
services and a tasks compute resource requirements, the software returns a list
of TES and DRS services (per file) that are rank-ordered according to
either increasing estimated costs or increasing estimates total processing
times.

## Install

Clone the repository

```bash
git clone git@github.com:elixir-europe/TEStribute.git
cd TEStribute
```

Install dependencies

```bash
virtualenv -p `which python3` venv
source venv/bin/activate
pip install -r requirements.txt
```

Install app

```bash
python setup.py develop
```

## Basic usage

`TEStribute` can be run in two ways:

### From the command line

In this use case, currently it is not possible to pass arguments directly. See
section "Advanced usage" below for a way how TEStribute can be configured to
run with different parameters.

```bash
python TEStribute/__init__.py
```

### Import `TEStribute` in another project/module

First install `TEStribute` (e.g., inside your projects virtual environment)
with:

```bash
pip install -e \
git+git@github.com:elixir-europe/TEStribute.git@master#egg=TEStribute
```

Then, in the Python module where you want to use `TEStribute`, add the
following code:

```py
from TEStribute import rank_services

rank_services()
```

## Advanced usage

When supplied without any arguments, the `rank_services()` function defined in
`__init__.py` uses default values from a config file. Currently, there are two
ways of running `TEStribute` with different arguments:

### Modify the configuration file

Edit the config file at `TEStribute/config/config.yaml`.

Then run `TEStribute` as described above.

### Call `rank_services()` with arguments

Follow the instructions above on how to install `TEStribute`. Then you can
simply pass arguments to the `rank_services()` function call, e.g.:

```py
rank_services(
    drs_ids=[
        "id_input_file_1",
        "id_input_file_2"
    ],
    resource_requirements={
        "cpu_cores": "2",
        "ram_gb": "8",
        "disk_gb": "10",
        "execution_time_min": "300"
    },
    tes_uris=[
        "https://some.tes.service/",
        "https://another.tes.service/"
    ],
    drs_uris=[
        "https://some.drs.service/",
        "https://another.drs.service/"
    ],
    mode="cost",
    auth_header=None
)
```

It is not necessary to pass all arguments. Omit any arguments to use the
corresponding default values as defined in `TEStribute/config/config.yaml` or,
alternatively, pass `None`.

## Tests

Unit tests can be run with the following command:

```bash
pytest
```
