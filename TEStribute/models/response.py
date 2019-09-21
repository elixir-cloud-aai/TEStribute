
"""
Object models for representing nested, dependent data structures.
"""
from copy import deepcopy
from itertools import product
import logging
from socket import (gaierror, gethostbyname)
from typing import (Dict, Iterable, List, Mapping, Set, Tuple)
from urllib.parse import urlparse

from ip2geotools.errors import InvalidRequestError

from TEStribute.errors import ResourceUnavailableError
from TEStribute.log import log_yaml
from TEStribute.models import (
    AccessUris,
    Costs,
    Currency,
    Duration,
    DrsObject,
    ServiceCombination,
    TaskInfo,
    TimeUnit,
)
import TEStribute.models.request as rq
from TEStribute.utils.service_calls import (
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
        request = rq.Request,
        timeout = float,
    ) -> None:
        # Get TES task info for resource requirements
        try:
            tes_task_info = fetch_tes_task_info(
                tes_uris=request.tes_uris,
                resource_requirements=request.resource_requirements,
                jwt=request.jwt,
                timeout=timeout,
            )
        except ResourceUnavailableError:
            raise

        # Get metadata for DRS input objects
        try:
            drs_object_info = fetch_drs_objects_metadata(
                drs_uris=request.drs_uris,
                drs_ids=request.drs_ids,
                jwt=request.jwt,
                timeout=timeout,
            )
        except ResourceUnavailableError:
            raise

        # Get combinations of access URIs for TES instances and objects
        self.access_uri_combinations = self.get_access_uri_combinations(
            task_info=tes_task_info,
            object_info=drs_object_info,
        )

        # Add service combinations
        self.service_combinations: List[ServiceCombination] = []
        for access_uris in self.access_uri_combinations:
                self.service_combinations.append(
                    ServiceCombination(
                        access_uris=access_uris,
                        cost_estimate=Costs(
                            amount=-1,
                            currency=Currency.BTC,
                        ),
                        rank=-1,
                        time_estimate=Duration(
                            duration=-1,
                            unit=TimeUnit.SECONDS,
                        ),
                    )
                )

        # Add warnings
        self.warnings: List[str] = []

        # Add request
        self.request = request


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "service_combinations": [
                c.to_dict() for c in self.service_combinations
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
        # Create pair of TES IP and object IP for each object and each access
        # URI combination
        combinations = [c.to_dict() for c in self.access_uri_combinations]
        ips: Dict[Tuple[int, str], Set[str]] = {}
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
                    ips[(index, key)] = frozenset([tes_ip, obj_ip])

        # Create unique set of IP pairs
        ips_unique: Dict[Set[str], List[Tuple[int, str]]] = {
            v: [] for v in ips.values()
        }
        for k, v in ips.items():
            ips_unique[v].append(k)

        # Calculate distances between all IPs
        distances_unique: Dict[Set[str], float] = {}
        self.distances_full: Dict[str, Dict] = {}
        ips_all = frozenset().union(*list(ips_unique.keys()))
        try:
            self.distances_full = ip_distance(*ips_all)
        except ValueError:
            pass
        for ip_set in ips_unique.keys():
            if len(ip_set) == 1:
                distances_unique[ip_set] = 0
            else:
                try:
                    distances_unique[ip_set] = \
                        self.distances_full["distances"][tuple(ip_set)]
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
        self.distances: List[Dict[str, float]] = [
            deepcopy({}) for i in range(len(self.access_uri_combinations))
        ]
        for ip_set, combinations in ips_unique.items():
            for combination in combinations:
                try:
                    self.distances[combination[0]][combination[1]] = \
                        distances_unique[ip_set]
                except KeyError:
                    pass
        
        # Check for and remove service combinations for which no distances
        # are available
        for index in reversed(range(len(self.distances))):
            if len(self.distances[index]) != len(self.request.drs_uris):
                warning = (
                    f"The following service combination was removed because " \
                    f"no or not all distances could be computed: " \
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
        # TODO: put here some "smartness" to reduce execution time for
        #       complex cases; implement later
        pass


    def estimate_costs(
        self,
    ) -> None:
        """

        """
        pass


    def estimate_times(
        self,
    ) -> None:
        """

        """
        pass


    def rank_combinations(
        self,
    ) -> None:
        """

        """
        # TODO: shuffle combinations if mode is 'random'
        pass
