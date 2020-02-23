"""
Object models for representing nested, dependent data structures.
"""
from copy import deepcopy
from itertools import product
import logging
import numpy as np
from random import shuffle
from socket import (gaierror, gethostbyname)
from typing import (Dict, Iterable, List, Mapping, Set, Tuple)
from urllib.parse import urlparse

from TEStribute.errors import ResourceUnavailableError
from TEStribute.models import (
    AccessUris,
    Costs,
    Currency,
    DrsObject,
    ServiceCombination,
    TaskInfo,
)
import TEStribute.models.request as rq
from TEStribute.utils.service_calls import (
    fetch_exchange_rates,
    fetch_drs_objects_metadata,
    fetch_tes_task_info,
    ip_distance,
)

logger = logging.getLogger("TEStribute")


class Response:
    """
    Response schema describing the endpoint's output.
    """
    def __init__(
        self,
        request=rq.Request,
        timeout: float = 3,
        target_currency: Currency = Currency.BTC,
    ) -> None:
        # Add attributes
        self.warnings: List[str] = []
        self.request = request
        self.timeout = timeout
        self.target_currency = target_currency

        # Get TES task info for resource requirements
        try:
            self.task_info = fetch_tes_task_info(
                tes_uris=request.tes_uris,
                resource_requirements=request.resource_requirements,
                jwt=request.jwt,
                timeout=self.timeout,
            )
        except ResourceUnavailableError:
            raise

        # Get currency exchange rates
        try:
            self.exchange_rates = fetch_exchange_rates(
                target_currency=target_currency.value,
                currencies=[c.value for c in Currency],
                amount=1.0,
            )
        except ResourceUnavailableError:
            raise

        # Convert currencies to base currency
        remove_tes: List = []
        for tes_uri, task_info in self.task_info.items():
            unsupported_currency = False
            costs = [
                task_info.estimated_compute_costs,
                task_info.estimated_storage_costs,
                task_info.unit_costs_data_transfer,
            ]
            for item in costs:
                if item.currency.value == self.target_currency.value:
                    continue

                elif item.currency.value not in self.exchange_rates or \
                        not self.exchange_rates[item.currency.value]:
                    unsupported_currency = True
                    logger.warning(
                        f"TES '{tes_uri}' provided costs in currency "
                        f"'{item.currency.value}', for which no exchange rate "
                        "to the configured base currency "
                        f"'{self.target_currency.value}' is available. "
                        "Skipped."
                    )
                    continue

                # Convert costs to base currency
                val = self.exchange_rates[item.currency.value]
                item.amount = item.amount / val  # type: ignore
                item.currency = Currency(target_currency)

            if unsupported_currency:
                remove_tes.append(tes_uri)
                continue

        # Remove TES instances that provide costs that cannot be compared
        for tes_uri in remove_tes:
            del self.task_info[tes_uri]

        # Get metadata for DRS input objects
        try:
            self.object_info = fetch_drs_objects_metadata(
                drs_uris=request.drs_uris,
                object_ids=request.object_ids,
                jwt=request.jwt,
                timeout=self.timeout,
            )
        except ResourceUnavailableError:
            raise

        # Determine object sizes
        self.object_sizes: Dict[str, int] = {}
        object_sizes: Dict[str, Set[int]] = {}
        for object_id, val in self.object_info.items():  # type: ignore
            object_sizes[object_id] = set()
            for drs_object in val.values():  # type: ignore
                object_sizes[object_id].add(drs_object.size)
        self.object_sizes = {
            object_id: int(list(sizes)[0])
            for object_id, sizes in object_sizes.items()
        }

        # Get combinations of access URIs for TES instances and objects
        self.access_uri_combinations = self.get_access_uri_combinations(
            task_info=self.task_info,
            object_info=self.object_info,
        )

        # Add service combinations
        self.service_combinations: List[ServiceCombination] = []
        for access_uris in self.access_uri_combinations:
            self.service_combinations.append(
                ServiceCombination(
                    access_uris=access_uris,
                    cost_estimate=Costs(
                        amount=-1,
                        currency=self.target_currency,
                    ),
                    rank=-1,
                    time_estimate=-1,
                )
            )
        self.service_combinations_sorted = self.service_combinations

    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "service_combinations": [
                c.to_dict() for c in self.service_combinations_sorted
            ],
            "warnings": self.warnings,
        }

    @staticmethod
    def get_access_uri_combinations(
        task_info: Mapping[str, TaskInfo],
        object_info: Mapping[str, Mapping[str, DrsObject]],
    ) -> List[AccessUris]:
        """
        Compiles all valid combinations of TES services and access URIs for
        each input object.

        :param task_info: TES TaskInfo objects for a set of TES URIs.
        :param object_info: DRS DrsObject objects for a set of DRS URIs (inner
                keys) and DRS IDs (outer keys).

        :return: List of AccessUri objects.
        """
        # Get all unique access URIs for each object
        access_uris: Dict[str, Iterable[str]] = {}
        for object_id, drs_info in object_info.items():
            object_uris: List[str] = []
            for object_metadata in drs_info.values():
                for access_method in object_metadata.access_methods:
                    object_uris.append(access_method.access_url.url)
            access_uris[object_id] = set(object_uris)

        # Add TES URIs
        access_uris["tes_uri"] = set(task_info.keys())

        # Assemble all combinations of access URIs
        keys, uris = zip(*access_uris.items())
        combinations = [dict(zip(keys, uri)) for uri in product(*uris)]
        uri_combinations = []
        for combination in combinations:
            uri_combinations.append(AccessUris(**combination))

        # Return list of combinations
        return uri_combinations

    def get_distances(
        self,
    ) -> None:
        """
        For each service combination computes the distance between the TES and
        each object. Removes any service combination for which not all
        distances can be computed.

        :return: An instance attribute `distances` of the following form is
        generated:

            [{
                'obj1': 123.5,
                'obj2': 2341.1,
                'total': 2464.6
            }, {
                'obj1': 1341.2,
                'obj2': 12512.3,
                'total': 13853.5
            }]

        The order of the list corresponds to that of attributes
        `access_uri_combinations` and `service_combinations`. The value
        indicated for key `total` is the sum of distances between TES and
        each of the objects (here: `obj1` and `obj2`).
        """
        self.distances_full: Dict[str, Dict] = {}
        self.distances: List[Dict[str, float]] = []

        # Do not continue if no input object metadata available
        if not self.object_info:
            return None

        # Create pair of TES IP and object IP for each object and each access
        # URI combination
        combinations = [c.to_dict() for c in self.access_uri_combinations]
        ips = {}
        for index in range(len(combinations)):
            try:
                tes_domain = urlparse(combinations[index]["tes_uri"]).netloc
                tes_ip = gethostbyname(tes_domain)
            except KeyError:
                continue
            except gaierror:
                continue
            for key, uri in combinations[index].items():
                if key != "tes_uri":
                    try:
                        obj_ip = gethostbyname(urlparse(uri).netloc)
                    except gaierror:
                        break
                    ips[(index, key)] = (tes_ip, obj_ip)

        # Create unique set of IP pairs
        ips_unique: Dict[Set[str], List[Tuple[int, str]]] = {
            v: [] for v in ips.values()  # type: ignore
        }
        for k, v in ips.items():
            ips_unique[v].append(k)  # type: ignore

        # Calculate distances between all IPs
        distances_unique: Dict[Set[str], float] = {}
        ips_all = frozenset().union(*list(ips_unique.keys()))  # type: ignore
        try:
            self.distances_full = ip_distance(*ips_all)
        except ValueError:
            pass
        for ip_tuple in ips_unique.keys():
            if len(set(ip_tuple)) == 1:
                distances_unique[ip_tuple] = 0
            else:
                try:
                    distances_unique[ip_tuple] = \
                        self.distances_full["distances"][ip_tuple]
                except KeyError:
                    pass

        # Reshape distances keys for logging
        keys = list(self.distances_full["distances"].keys())
        keys = ['|'.join([str(i) for i in t]) for t in keys]
        self.distances_full["distances"] = dict(zip(
            keys,
            list(self.distances_full["distances"].values()))
        )

        # Map distances back to each access URI combination
        self.distances = [
            deepcopy({}) for i in range(len(self.access_uri_combinations))
        ]
        for ip_set, combinations in ips_unique.items():  # type: ignore
            for combination in combinations:
                try:
                    self.distances[combination[0]][combination[1]] = \
                        distances_unique[ip_set]
                except KeyError:
                    pass

        # Check for and remove service combinations for which no distances
        # are available
        for index in reversed(range(len(self.distances))):
            if len(self.distances[index]) != len(self.request.object_ids):
                warning = (
                    "The following service combination was removed because "
                    "no or not all distances could be computed: "
                    f"{self.service_combinations[index].access_uris.to_dict()}"
                )
                self.warnings.append(warning)
                logger.warn(warning)
                del self.access_uri_combinations[index]
                del self.distances[index]
                del self.service_combinations[index]

        # Add distance totals
        for combination in self.distances:
            combination['total'] = sum(combination.values())

    def filter_service_combinations(
        self,
    ) -> None:
        """
        """
        # Ensure that there are any service combinations left
        if not self.service_combinations:
            raise ResourceUnavailableError(
                "No valid service combinations available."
            )

    def estimate_costs(
        self,
    ) -> None:
        """
        Calculates object transfer costs and adds it to the compute costs to
        calculate the total costs, then updates `cost_estimate` attribute of
        `service_combinations` attribute.
        """
        # Iterate over service combinations
        for index in range(len(self.service_combinations)):

            # Get TES URI of current service combination
            tes_uri = self.service_combinations[index].access_uris.tes_uri
            costs_transfer: float = 0
            for object_id in self.request.object_ids:

                # Calculate transfer costs from object size, distance between
                # TES and object and rate
                costs_transfer += (
                    self.object_sizes[object_id] *
                    self.distances[index][object_id] *
                    self.task_info[tes_uri].unit_costs_data_transfer.amount /
                    1e12
                )

            # Update cost estimate with sum of compute, storage and transfer
            # costs
            self.service_combinations[index].cost_estimate.amount = (
                self.task_info[tes_uri].estimated_compute_costs.amount +
                self.task_info[tes_uri].estimated_storage_costs.amount +
                costs_transfer
            )

    def estimate_times(
        self,
    ) -> None:
        """
        Updates `time_estimate` attribute of `service_combinations` attribute
        with the sum of the estimated queue time and the specified task
        execution time, in minutes.
        """
        # Iterate over service combinations
        for index in range(len(self.service_combinations)):

            # Get TES URI of current service combination
            tes_uri = self.service_combinations[index].access_uris.tes_uri

            # Update time estimate with sum of queue and execution time
            self.service_combinations[index].time_estimate = (
                float(self.task_info[tes_uri].estimated_queue_time_sec) +
                float(self.request.resource_requirements.execution_time_sec)
            )

    def rank_combinations(
        self,
    ) -> None:
        """
        """
        # Get mode
        mode = self.request.mode_float

        # Calculate scores and ranks
        if mode >= 0:

            # Get all time estimates
            times = np.array([
                combination.time_estimate for combination in
                self.service_combinations
            ])

            # Get all cost esimates
            costs = np.array([
                combination.cost_estimate.amount for combination in
                self.service_combinations
            ])

            # Normalize and weight times & costs
            times_weight = times / times[0] * mode
            costs_weight = costs / costs[0] * (1 - mode)

            # Calculate score
            scores = times_weight + costs_weight

            # Order scores and reorder ranks
            order = scores.argsort()
            ranks = np.empty_like(order)
            ranks[order] = np.arange(len(scores)) + 1  # type: ignore
            self.ranks = ranks.tolist()  # type: ignore

            # Add scores to instance attributes
            self.scores = scores.tolist()

        # Shuffle ranks and set scores to -1 (for mode 'random')
        else:
            self.scores = [-1 for i in self.service_combinations]
            self.ranks = list(
                range(1, len(self.service_combinations) + 1)
            )
            shuffle(self.ranks)

        # Rank service combinations
        for index in range(len(self.service_combinations)):
            self.service_combinations[index].rank = self.ranks[index]

        # Add sorted list of service combinations
        self.service_combinations_sorted = sorted(
            self.service_combinations, key=lambda k: k.rank
        )
