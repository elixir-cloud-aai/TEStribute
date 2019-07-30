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

## Usage

```bash
cd TEStribute
python __init__.py
```

## Current functionality

The `main()` function defined in `__init__.py` defines a test case for function
`rank_services()` which returns a dict of rank-ordered TES & DRS services for a
given task. The service writes logging information to a file `log/tes_log.log`.
