# TEStribute

[![Apache License](https://img.shields.io/badge/license-Apache%202.0-orange.svg?style=flat&color=important)](http://www.apache.org/licenses/LICENSE-2.0)

Task distribution for GA4GH TES instances.

## Synopsis

Proof of concept implementation of a **task distribution** logic for a federated
network of [GA4GH][1] [Task Execution Service] (TES) instances.

![TEStribute_working]

## Usage

You can use `TEStribute` in three ways:

- Call the **HTTP API service**, e.g. with `curl`:

```bash
curl -X POST SERVICE_URI -H "Content-Type: application/json" -d PAYLOAD
```

- Call the **console script**:

```bash
testribute [-h] --tes-uri URI --cpu-cores INT --ram-gb FLOAT --disk-gb FLOAT
           --execution-time-sec INT [--jwt TOKEN] [--object-id ID] [--drs-uri
           URI] [-m MODE] [-v]
```

- Call the **main function** directly, from within your Python code:

```py
from TEStribute import rank_services

rank_services(...)
```

## Implementation details

Given a set of available [GA4GH][1] [Task Execution Service] (TES) instances, a
task's compute resource requirements, the [Data Repository Service] (DRS)
object identifiers of all task inputs (if any), and a list of DRS instances
where these objects might be obtained from, TEStribute returns a list of
combinations of TES instances and input object locations, rank-ordered according
to either increasing *estimated total costs*, increasing *estimated total
processing times*, or a weighting factor that balances both of these
properties.

The application currently relies on [modifications] to the TES specifications
and assumes that DRS object identifiers are globally unique (i.e., a given
identifier will point to the same exact file on any DRS instance), which is
not warranted by current DRS specs. More detailed information on these
requirements is available at [mock-TES] and [mock-DRS], mockup services which
implement these modifications/assumptions. The corresponding clients [TES-cli]
and [DRS-cli] are used within `TEStribute` to interact with these services.

## Installation

### Deploying the API service

Ensure you have the following software installed:

- [Docker](https://www.docker.com/) (18.06.1-ce, build e68fc7a)
- [docker-compose](https://docs.docker.com/compose/) (1.23.1, build b02f1306)
- [Git](https://git-scm.com/) (tested with version 2.17.1)

Clone repository and start Docker service

```bash
git clone https://github.com/elixir-europe/TEStribute.git app
cd app
docker-compose up --build --detach
```

You can explore the HTTP API via the Swagger UI:

```bash
firefox http://localhost:7979/ui/
```

### CLI usage & import

Ensure you have the following software installed:

- [Python](https://www.python.org) (tested with version 3.6.8)
- [pip](https://pip.pypa.io/en/stable/) (tested with version 19.2.2)

Install package and `testribute` console script:

```bash
pip install TEStribute
```

## Extended usage

### Options

The following properties/options are available when running TEStribute,
regardless of whether the software is run as an HTTP API service, as a console
script or directly from within your Python code. The CLI option is indicated
in parentheses in those cases where it differs from API / import usage:

- `object_ids` (`object-id`): DRS IDs of objects required by the task. When
  using the console script, indicate the option multiple times to pass multiple
  arguments.
- `drs_uris` (`drs-id`): URIs of DRS instances that objects may be read from or
  written to. When using the console script, indicate the option multiple times
  to pass multiple arguments.
- `mode`: Defines how service combinations are ranked, either by 'cost', 'time'
  or both. For the latter, specify a number between 0 and 1, with the boundaries
  representing weights at which services are ranked entirely by cost and time,
  respectively. It is also possible to randomize rankings (specify 'random' or
  -1).
- `resource_requirements` (not available as CLI option, use properties
  directly): Map of resources required for the task:
  - `cpu_cores` (`cpu-cores`): Requested number of CPUs.
  - `disk_gb` (`disk-gb`): Requested disk size in gigabytes (GB).
  - `execution_time_sec` (`execution-time-sec`): Requested execution time in
    seconds (s).
  - `preemptible` (not available as CLI option): Is the task allowed to run on
    preemptible compute instances (e.g. AWS Spot)? Currently not used.
  - `ram_gb`: Requested RAM required in gigabytes (GB).
  - `zones` (not available as CLI option): Request that the task be run in
    these compute zones. Currently not used.
- `tes_uris` (`tes-uri`): URIs of known TES instances that the task may be
  computed on. When using the console script, indicate the option multiple times
  to pass multiple arguments.
- `jwt`: JSON Web Token (JWT) bearer token that is attached as an
  `Authorization` request header, following the keyword `Bearer`, to any
  outgoing service call, if provided, in order to ascertain whether the user has
  permissions to access resources and/or whether user-specific policies or
  contstraints apply (e.g., custom prices, discounts, quotas). Note that when
  using TEStribute through the HTTP API, this property is not available.
  Instead, the token value itself needs to be passed as an `Authorization`
  request header, also following the `Bearer` keyword.

> For more details, including typing information, explore the [API definition],
> which also forms the basis for validating CLI arguments and the inputs to the
> `rank_services()` function.

### Example calls

The following are equivalent calls for either of the TEStribute entry points
defined above. Note that the provided TES and DRS URIs point to test instances
of the services which may or may not be up and running at any given time.
Therefore, the success of the calls cannot be guaranteed.

#### API service call payload (JSON)

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
    "execution_time_sec": 1800,
    "ram_gb": 1
  },
  "tes_uris": [
    "http://131.152.229.70/ga4gh/tes/v1/",
    "http://193.166.24.111/ga4gh/tes/v1/"
  ]
}
```

#### Console script call

```bash
testribute \
  --tes-uri="http://131.152.229.70/ga4gh/tes/v1/" \
  --tes-uri="http://193.166.24.111/ga4gh/tes/v1/" \
  --cpu-cores=1 \
  --ram-gb=1 \
  --disk-gb=1 \
  --execution-time-sec=1800 \
  --object-id="a001" \
  --object-id="a002" \
  --drs-id="http://131.152.229.71/ga4gh/drs/v1/" \
  --drs_id="http://193.166.24.114/ga4gh/drs/v1/" \
  --mode=0.5
```

#### Function call

```py
from TEStribute import rank_services

rank_services(
    object_ids=[
        "a001",
        "a002"
    ],
    resource_requirements={
        "cpu_cores": 1,
        "ram_gb": 1,
        "disk_gb": 1,
        "execution_time_sec": 1800
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
    jwt=None
)
```

### Return types

#### Success

Upon success, the API service returns a JSON object such as this:

```json
{
  "service_combinations": [
    {
      "access_uris": {
        "a001": "ftp://ftp.ensembl.org/pub/release-96/fasta/homo_sapiens/dna//Homo_sapiens.GRCh38.dna.chromosome.19.fa.gz",
        "a002": "ftp://ftp.ensembl.org/pub/release-81/bed/ensembl-compara/11_teleost_fish.gerp_constrained_elements/gerp_constrained_elements.tetraodon_nigroviridis.bed.gz",
        "tes_uri": "http://193.166.24.111/ga4gh/tes/v1/"
      },
      "cost_estimate": {
        "amount": 294727.1443451331,
        "currency": "EUR"
      },
      "rank": 1,
      "time_estimate": 2514
    },
    {
      "access_uris": {
        "a001": "ftp://ftp.ensembl.org/pub/release-96/fasta/homo_sapiens/dna//Homo_sapiens.GRCh38.dna.chromosome.19.fa.gz",
        "a002": "ftp://ftp.ensembl.org/pub/release-81/bed/ensembl-compara/11_teleost_fish.gerp_constrained_elements/gerp_constrained_elements.tetraodon_nigroviridis.bed.gz",
        "tes_uri": "http://131.152.229.70/ga4gh/tes/v1/"
      },
      "cost_estimate": {
        "amount": 294697.1938522269,
        "currency": "EUR"
      },
      "rank": 2,
      "time_estimate": 3298
    }
  ],
  "warnings": []
}
```

You can check out the `Response` model in the [API definition] for more details.
For the other entry points, the general response upon success is the same, but
provided in different ways. When calling `rank_services()` directly from within
Python code, the response is an instance of Python class `Response`, which is
based on the corresponding model in the [API definition] and defined in module
[TEStribute.models.response]. It can be converted to dictionary form with:

```py
response = rank_service(...)
response.to_dict()
```

It can be further converted to JSON with:

```py
import json

json.dumps(response.to_dict())
```

When using the `testribute` console script, the JSONified response is printed to
`STDOUT`.

#### Failure

In case of failure, the API service returns a JSON object of the following form:

```json
{
  "code": 400,
  "errors": [
    {
      "reason": "werkzeug.exceptions.BadRequest",
      "message": [
        "Services cannot be ranked. None of the specified TES instances provided any task info."
      ]
    }
  ],
  "message": "The request caused an error."
}
```

When using the console script `testribute`, an error will lead to the script
exiting with a non-zero return code. In addition, warnings and errors are
written to the log which is streamed to `STDERR`, e.g.:

```console
[WARNING] TES unavailable: the provided URI 'http://i.do.not.exist/' could not be resolved.
[ERROR] ResourceUnavailableError: Services cannot be ranked. None of the specified TES instances provided any task info.
```

When calling `rank_services()` directly from within Python code, traceback
information for any error is provided, too. For
example:

```console
[WARNING] TES unavailable: the provided URI 'http://i.do.not.exist/' could not be resolved.
Traceback (most recent call last):
  File "<stdin>", line 21, in <module>
  File "/home/uniqueg/Dropbox/repos/TEStribute/TEStribute/__init__.py", line 129, in rank_services
    target_currency=models.Currency[config["target_currency"]],
  File "/home/uniqueg/Dropbox/repos/TEStribute/TEStribute/models/response.py", line 55, in __init__
    timeout=self.timeout,
  File "/home/uniqueg/Dropbox/repos/TEStribute/TEStribute/utils/service_calls.py", line 311, in fetch_tes_task_info
    "Services cannot be ranked. None of the specified TES instances " \
TEStribute.errors.ResourceUnavailableError: Services cannot be ranked. None of the specified TES instances provided any task info.
```

### Configuration

It is possible to configure some settings of the app, e.g., how JWTs are parsed,
processed and forwarded or in which prices costs are reported, by modifying the
the [config file](TEStribute/config/config.yaml) before starting the service /
running TEStribute.

## Testing

Unit and integration tests can be run with the following command:

```bash
pytest
```

> Note that test coverage is currently sparse and tests are unstable.

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
[API definition]: TEStribute/specs/schema.TEStribute.openapi.yaml
[code of conduct]: CODE_OF_CONDUCT.md
[config]: TEStribute/config/config.yaml
[contributing guidelines]: CONTRIBUTING.md
[Data Repository Service]: <https://github.com/ga4gh/data-repository-service-schemas>
[DRS-cli]: <https://github.com/elixir-europe/DRS-cli>
[ELIXIR Cloud and AAI]: <https://elixir-europe.github.io/cloud/>
[Git]: <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>
[logo banner]: images/logo-banner.png
[mock-TES]: <https://github.com/elixir-europe/mock-TES>
[modififications]: <https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml>
[mock-DRS]: <https://github.com/elixir-europe/mock-DRS>
[`mode.Mode`]: TEStribute/models.py
[organization]: <https://summerofcode.withgoogle.com/organizations/6643588285333504/>
[OpenAPI]: <https://swagger.io/specification/>
[pip]: <https://pip.pypa.io/en/stable/installing/>
[Python]: <https://www.python.org/downloads/>
[semantic versioning]: <https://semver.org/>
[Task Execution Service]: <https://github.com/ga4gh/task-execution-schemas>
[TES-cli]: <https://github.com/elixir-europe/TES-cli>
[TEStribute.models.response]: TEStribute/models/response.py
[virtualenv]: <https://virtualenv.pypa.io/en/stable/installation/>
[TEStribute_working]:images/schema.png
