
"""
Object models for representing nested, dependent data structures.
"""
from itertools import product
import logging
from typing import (Dict, Iterable, List, Mapping)

from TEStribute.errors import ResourceUnavailableError
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
        self.warnings: Iterable[str] = []


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
        Should take the similar input to the rak_services and return any random list of usable TES & DRS services

        :param task_info: Dict of the form
        :param object_info: Dict of form drs_uri's and drs_id's

        :return: Dict of the form
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

        """
        pass


    def filter_service_combinations(
        self,
    ) -> None:
        """

        """
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
