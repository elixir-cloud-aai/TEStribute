"""
Exposes TEStribute main function rank_services()
"""
import logging
import os
from typing import (Iterable, Mapping, Optional, Union)


from TEStribute import models
import TEStribute.models.request as rq
import TEStribute.models.response as rs
from TEStribute.config import config_parser
from TEStribute.log import (log_yaml, setup_logger)

# Set up logging
log_file = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "log",
        "testribute.log"
    )
)
logger = setup_logger("TEStribute", logging.DEBUG)
logging.captureWarnings(capture=True)


def rank_services(
    jwt: Optional[str] = None,
    object_ids: Iterable = [],
    drs_uris: Iterable = [],
    mode: Union[float, int, models.Mode, str] = 0.5,
    resource_requirements: Mapping = {},
    tes_uris: Iterable = [],
) -> rs.Response:
    """
    Main function that returns a rank-ordered list of GA4GH TES and DRS
    services to use when submitting a TES task to decrease total costs and or
    time. Default values for all parameters are available in and derived from
    the config file `config/config.yaml`, if not provided.

    :param jwt: JSON Web Token to be passed to any TES/DRS calls in order to
            ascertain whether the user has permissions to access service
            specified in `object_ids`, `tes_instances` and `drs_instances`,
            whether there are particular constraints or special provisions in
            place that apply to the user (e.g., custom prices).
    :param object_ids: List of DRS identifiers of input files required for the
            task. Can be derived from `inputs` property of the `tesTask`
            model of the GA4GH Task Execution Service schema described here:
            https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution.swagger.yaml
    :param drs_uris: List of root URIs to known DRS instances.
    :param resource_requirements: Dictionary of resources required for the
            task; of the form described in the `tesResources` model of the
            _modified_ GA4GH Task Execution Service schema as described here:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
            Note that the `preemptible` and `zones` properties are currently
            not used.
    :param mode: Either a `mode.Mode` enumeration object, one of its members
            'cost', 'time' or 'random', or one of its values 0, 1, -1,
            respetively. Depending on the mode, services are rank-ordered by
            increasing cost or time, or are randomized for testing/control
            purposes; it is also possible to pass a float between 0 and 1;
            in that case, the value determines the weight between cost (0)
            and time (1) optimization.
    :param tes_uris: List of root URIs to known TES instances.

    :return: an ordered list of dictionaries of TES and DRS instances; inner
            dictionaries are of the form:
                {
                    "rank": "integer",
                    "TES": "TES_URL",
                    [object_id]: "DRS_URL",
                    [object_id]: "DRS_URL",
                    ...
                    "output_files": "DRS_URL",
                }
            where [object_id] entries are taken from parameter `object_ids`.
    """
    # Parse config file
    logger.debug("=== CONFIG ===")
    config = config_parser()
    log_yaml(
        level=logging.DEBUG,
        logger=logger,
        config=config,
    )

    # Create Request object
    log_yaml(
        header="=== USER INPUT ===",
        level=logging.INFO,
        logger=logger,
        object_ids=object_ids,
        drs_uris=drs_uris,
        mode=mode,
        resource_requirements=resource_requirements,
        tes_uris=tes_uris,
    )
    request = rq.Request(
        object_ids=object_ids,
        drs_uris=drs_uris,
        mode=mode,
        resource_requirements=models.ResourceRequirements(
            **resource_requirements
        ),
        tes_uris=tes_uris,
        authorization_required=config["security"]
        ["authorization_required"],
        jwt=jwt,
        jwt_config=config["security"]["jwt"],
    )
    logger.debug("=== VALIDATION ===")
    log_yaml(
        level=logging.DEBUG,
        logger=logger,
        **request.to_dict(),
    )

    # Create Response object
    logger.debug("=== INITIALIZE RESPONSE ===")
    response = rs.Response(
        request=request,
        timeout=config["timeout"],
        target_currency=models.Currency[config["target_currency"]],
    )
    log_yaml(
        level=logging.DEBUG,
        logger=logger,
        **response.to_dict()
    )
    log_yaml(
        header="=== CURRENCY EXCHANGE RATES ===",
        level=logging.DEBUG,
        logger=logger,
        target_currency=response.target_currency.value,
        object_info=response.exchange_rates,
    )
    log_yaml(
        header="=== TES TASK INFO ===",
        level=logging.DEBUG,
        logger=logger,
        object_info={k: v.to_dict() for k, v in response.task_info.items()},
    )
    log_yaml(
        header="=== DRS OBJECT INFO ===",
        level=logging.DEBUG,
        logger=logger,
        object_info={
            object_id: {
                key: metadata.to_dict() for key, metadata in service.items()
            } for object_id, service in response.object_info.items()
        },
    )
    log_yaml(
        header="=== OBJECT SIZES ===",
        level=logging.DEBUG,
        logger=logger,
        object_info=response.object_sizes,
    )

    # Compute distances
    response.get_distances()
    log_yaml(
        header="=== DISTANCES ===",
        level=logging.DEBUG,
        logger=logger,
        distances_detailed=response.distances_full,
        distances=response.distances,
    )

    # Filter service combinations
    response.filter_service_combinations()

    # Estimate costs
    response.estimate_costs()

    # Estimate total task time
    response.estimate_times()

    # Rank service combinations
    response.rank_combinations()
    log_yaml(
        header="=== SCORES ===",
        level=logging.DEBUG,
        logger=logger,
        scores=[str(i) for i in response.scores],
    )

    # Return response object
    log_yaml(
        header="=== OUTPUT ===",
        level=logging.INFO,
        logger=logger,
        **response.to_dict()
    )
    return response
