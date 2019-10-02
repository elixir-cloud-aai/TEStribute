# TEStribute

Task distribution for GA4GH TES services.

## Synopsis

Proof of concept implementation of a **task distribution** logic for a federated
network of [GA4GH][1] [Task Execution Service] (TES) instances.

## Usage

`TEStribute` can be run in two ways:

### From a Python module

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

### From the command line

```bash
python TEStribute/__init__.py
```

> In this use case, currently it is not possible to pass arguments directly. See
> section [Extended usage](#Extended-usage) below for ways how `TEStribute` can
> be run with different parameters.

## Implementation details

Given lists of available [GA4GH][1] [Task Execution Service] (TES) and [Data
Repository Service] (DRS) instances, the DRS identifiers for all input files,
and a task's compute resource requirements (e.g., extracted from a `POST /tasks`
TES request), the software returns a list of combinations of TES and DRS
instances (per input file) that are rank-ordered according to either increasing
estimated **total costs**, increasing estimated **total processing times**, or a
weighting factor that balances both of these parameters.

The application currently relies on [modified TES specifications] and the
assumption that DRS file identifiers are globally unique (i.e., a given
identifier will point to the same exact file on any DRS instance). More detailed
information on these requirements is available at [mock-TES] and [mock-DRS],
mockup services which implement these modifications/assumptions. The
corresponding clients [TES-cli] and [DRS-cli] are used within `TEStribute`
to interact with these services.

The diagram shown below shows how the TEStribute works at the moment.
![TEStribute_working]

## Installation

### API service (dockerized)

Ensure you have the following software installed:

* [Docker](https://www.docker.com/) (18.06.1-ce, build e68fc7a)
* [docker-compose](https://docs.docker.com/compose/) (1.23.1, build b02f1306)
* [Git](https://git-scm.com/) (tested with version 2.17.1)

> Note: These are the versions used for development/testing. Other versions
> may or may not work.

Clone repository and start Docker service

```bash
git clone https://github.com/elixir-europe/proTES.git app
cd app
docker-compose up --build --detach
```

Visit Swagger UI

```bash
firefox http://localhost:7979/ui/
```

### For CLI usage & imports

Ensure you have the following software installed:

* [Git](https://git-scm.com/) (tested with version 2.17.1)
* [Python](https://www.python.org) (tested with version 3.6.8)
* [pip](https://pip.pypa.io/en/stable/) (tested with version 19.2.2)
* [virtualenv](https://virtualenv.pypa.io/en/latest/)
  (tested with version 15.1.0)

> Note: These are the versions used for development/testing. Other versions
> may or may not work.

Clone repository, install app & dependencies

```bash
git clone git@github.com:elixir-europe/TEStribute.git app
cd app
virtualenv -p `which python3` venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py develop
```

## Extended usage

When supplied without any arguments, the `rank_services()` function defined in
`__init__.py` uses default values from a [config] file. Currently, there are two
ways of running `TEStribute` with different arguments:

### Call `rank_services()` with arguments

When [importing](#From-a-Python-module) `TEStribute`, pass any desired arguments
to the `rank_services()` function, which defines the following parameters:

* **`object_ids`**: List of DRS identifiers of input files required for the task.
  Can be derived from `inputs` property of the `tesTask` model of the [GA4GH]
  [Task Execution Service] schema described here.
* **`resource_requirements`**: Dictionary of resources required for the task.
  The required format is defined in the `tesResources` model of the [modified
  TES specifications] defined in [mock-TES]. Note that the `preemptible` and
  `zones` properties are currently not used.
* **`tes_uris`**: A list of root URIs to known TES instances.
* **`drs_uris`**: A list of root URIs to known DRS instances.
* **`mode`**: Either a [`mode.Mode`] enumeration object, one of its members
  `cost`, `time` or `random`, or one of its values `0`, `1`, `-1`, respetively.
  Depending on the mode, _valid_ combinations of TES and DRS services are
  rank-ordered by increasing cost or time, or are randomized for testing/control
  purposes. Apart from the discrete states, it is also possible to pass a float
  between `0` and `1`. In that case, the ordering of services is balanced
  between cost and time optimization (i.e., the closer to `1`, the more time
  efficiency will be considered).
* **`mode`**: Depending on the mode, _valid_ combinations of TES and DRS
  instances are rank-ordered by increasing cost or time, or are randomized for
  testing/control purposes. When passing a `float` (see below), the ordering of
  services is balanced between cost and time optimization, with values closer to
  `0` (`1`) leading to a more cost (time) efficient outcome. Valid arguments
  are:
  * A [`mode.Mode`] enumeration object
  * Members of [`mode.Mode`], currently `cost`, `time` or `random`
  * Values of [`mode.Mode`], currently `0`, `1`, `-1`, corresponding to `cost`,
    `time` and `random`, respectively
  * A `float` between `0` and `1`
* **`auth_header`**: Bearer (authorization) token to be passed to any TES/DRS
  calls in order to ascertain whether the user has permissions to access
  resources provided by the services specified via the `tes_uris` and `drs_uris`
  arguments, and whether there are particular constraints or provisions in place
  for the given user (e.g., custom prices, quotas). Currently not implemented.

#### Example call

##### API service

```json
{
  "object_ids": [
    "a001",
    "a002"
  ],
  "drs_uris": [
    "http://131.152.229.71/ga4gh/drs/v1/",
    "http://193.166.24.114/ga4gh/drs/v1/"
  ],
  "mode": 0.5,
  "resource_requirements": {
    "cpu_cores": 1,
    "disk_gb": 1,
    "execution_time_sec": 30,
    "ram_gb": 1
  },
  "tes_uris": [
    "http://131.152.229.70/ga4gh/tes/v1/",
    "http://193.166.24.111/ga4gh/tes/v1/"
  ]
}
```

##### CLI

Coming soon...

In this execution mode, it is not necessary to pass arguments for all
parameters. Omit any arguments to use the corresponding default values as
defined in the [config] file.

##### Importing `rank_services()`

```py
from TEStribute import rank_services()

rank_services(
    object_ids=[
        "a001",
        "a002"
    ],
    resource_requirements={
        "cpu_cores": 1,
        "ram_gb": 1,
        "disk_gb": 1,
        "execution_time_sec": 30
    },
    tes_uris=[
        "http://131.152.229.70/ga4gh/tes/v1/",
        "http://193.166.24.111/ga4gh/tes/v1/"
    ],
    drs_uris=[
        "http://131.152.229.71/ga4gh/drs/v1/",
        "http://193.166.24.114/ga4gh/drs/v1/"
    ],
    mode=0.5,
    auth_header=None
)
```

In this execution mode, it is not necessary to pass arguments for all
parameters. Omit any arguments to use the corresponding default values as
defined in the [config] file or, alternatively, pass `None`.

#### Return type

The function returns an ordered list of dictionaries of the form:

```py
{
    "rank": "integer",
    "TES": "TES_URL",
    object_id_1: "DRS_URL",
    object_id_2: "DRS_URL",
    ...
    "output_files": "DRS_URL",
}
```

where `[object_id]` entries are taken from parameter `object_ids`.

### Modify the configuration file

Edit the config file at `TEStribute/config/config.yaml`.

Then run `TEStribute` as described above.

## Testing

Unit and integration tests can be run with the following command:

```bash
pytest
```

## Contributing

This project is a community effort and lives off your contributions, be it in
the form of bug reports, feature requests, discussions, or fixes and other code
changes. Please read the [contributing guidelines] if you want to contribute.
And please mind the [code of conduct] for all interactions with the community.

## Versioning

Development of the app is currently still in alpha stage, and current versioning
is for internal use only. In the future, we are aiming to adopt [semantic
versioning] that is synchronized to the versioning of [mock-TES], [TES-cli],
[mock-DRS], and [DRS-cli] in order to ensure that these apps will be compatible
as long as both their major and minor versions match.

## License

This project is covered by the [Apache License 2.0] also available [shipped
with this repository](LICENSE).

## Contact

Please contact the [project leader](mailto:alexander.kanitz@sib.swiss) for
inquiries, proposals, questions etc. that are not covered by the
[Contributing](#Contributing) section.

## Acknowledgments

The project is a collaborative effort under the umbrella of the [ELIXIR Cloud
and AAI] group. It was started during the [2019 Google Summer of Code] as part
of the [Global Alliance for Genomics and Health][1] [organization].

![logo banner]

[1]: <https://www.ga4gh.org/>
[2019 Google Summer of Code]: <https://summerofcode.withgoogle.com/projects/#6613336345542656>
[Apache License 2.0]: <https://www.apache.org/licenses/LICENSE-2.0>
[code of conduct]: CODE_OF_CONDUCT.md
[config]: TEStribute/config/config.yaml
[contributing guidelines]: CONTRIBUTING.md
[Data Repository Service]: <https://github.com/ga4gh/data-repository-service-schemas>
[DRS-cli]: <https://github.com/elixir-europe/DRS-cli>
[ELIXIR Cloud and AAI]: <https://elixir-europe.github.io/cloud/>
[Git]: <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>
[logo banner]: logos/logo-banner.svg
[mock-TES]: <https://github.com/elixir-europe/mock-TES>
[modified TES specifications]: <https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml>
[mock-DRS]: <https://github.com/elixir-europe/mock-DRS>
[`mode.Mode`]: TEStribute/models.py
[organization]: <https://summerofcode.withgoogle.com/organizations/6643588285333504/>
[OpenAPI]: <https://swagger.io/specification/>
[pip]: <https://pip.pypa.io/en/stable/installing/>
[Python]: <https://www.python.org/downloads/>
[semantic versioning]: <https://semver.org/>
[Task Execution Service]: <https://github.com/ga4gh/task-execution-schemas>
[TES-cli]: <https://github.com/elixir-europe/TES-cli>
[virtualenv]: <https://virtualenv.pypa.io/en/stable/installation/>
[TEStribute_working]:infographics/TESTribute_working.png
