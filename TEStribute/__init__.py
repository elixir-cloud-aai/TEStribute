"""
Exposes TEStribute main function rank_services()
"""
import logging
import os
from typing import (Iterable, Mapping, Optional, Union)

from werkzeug.exceptions import Unauthorized

from TEStribute import models
import TEStribute.models.request as rq
import TEStribute.models.response as rs
from TEStribute.config import config_parser
from TEStribute.errors import ValidationError
from TEStribute.log import (log_yaml, setup_logger)

# Set up logging
log_file = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "log", "testribute.log")
)
logger = setup_logger("TEStribute", log_file, logging.DEBUG)


def rank_services(
    jwt: Optional[str] = None,
    drs_ids: Iterable = [],
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
            specified in `drs_ids`, `tes_instances` and `drs_instances`, whether
            there are particular constraints or special provisions in place that
            apply to the user (e.g., custom
            prices). Currently not implemented.
    :param drs_ids: List of DRS identifiers of input files required for the
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
                    [drs_id]: "DRS_URL",
                    [drs_id]: "DRS_URL",
                    ...
                    "output_files": "DRS_URL",
                }
            where [drs_id] entries are taken from parameter `drs_ids`.
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
        level=logging.DEBUG,
        logger=logger,
        drs_ids=drs_ids,
        drs_uris=drs_uris,
        mode=mode,
        resource_requirements=resource_requirements,
        tes_uris=tes_uris,
    )
    try:
        request = rq.Request(
            drs_ids=drs_ids,
            drs_uris=drs_uris,
            mode=mode,        
            resource_requirements=models.ResourceRequirements(
                **resource_requirements
            ),
            tes_uris=tes_uris,
            authorization_required=config["security"]["authorization_required"],
            jwt=jwt,
            jwt_config=config["security"]["jwt"],
        )
    except Unauthorized:
        raise

    # Validate input parameters
    logger.debug("=== VALIDATION ===")
    try:
        request.validate()
    except ValidationError:
        raise
    log_yaml(
        level=logging.DEBUG,
        logger=logger,
        **request.to_dict(),
    )

    # Create Response object
    logger.debug("=== OUTPUT ===")
    response = rs.Response(
        request=request,
        timeout=config["timeout"],
    )
    log_yaml(
        level=logging.DEBUG,
        logger=logger,
        **response.to_dict()
    )

    # Return response
    return response


#    # Get valid TES-DRS combinations
#    # TODO: Use model/class for return object
#    # TODO: Add to constructor of Response
#    valid_service_combos = get_valid_service_combinations(
#        task_info=tes_task_info,
#        object_info=drs_object_info,
#    )
#
#    # Compute distances
#    # TODO: Add to constructor of Response
#    tes_object_distances = estimate_distances(
#        combinations=valid_service_combos,
#    )
#
#    # Filter service combinations
#    # TODO: Add to constructor of Service Combinations
#
#    # Compute cost estimates
#    # TODO: Should be method of class ServiceCombinations
#    if models.Mode["cost"].value <= request.mode < models.Mode["time"].value:
#        tes_costs = estimate_costs(
#            task_info=tes_task_info,
#            object_info=drs_object_info,
#            distances=tes_object_distances,
#        )
#    else: tes_costs = {}
#
#    # Compute time estimates
#    # TODO: Should be method of class ServiceCombinations
#    if models.Mode["cost"].value < request.mode <= models.Mode["time"].value:
#        tes_times = estimate_times(
#            task_info=tes_task_info,
#            object_info=drs_object_info,
#            distances=tes_object_distances,
#        )
#    else: tes_times = {}
#    mode: float = float(request.mode)
#    # Rank by costs/times
#    # TODO: Should be method of class ServiceCombinations
#    ranked_services = rank_order.cost_time(
#        costs=tes_costs,
#        times=tes_times,
#        weight=request.mode,
#    )
#
#    # Randomize ranks
#    # TODO: Should be method of class ServiceCombinations
#    if mode == models.Mode["random"].value:
#        ranked_services = rank_order.randomize(
#            uris=tes_uris,
#            object_info=drs_object_info,
#        )
#    
#    # Catch other run modes
#    else:
#        logger.critical(
#            (
#                "Task cannot be computed: no ranking function defined for "
#                "mode: {mode}."
#            ).format(mode=mode)
#        )
#        raise ValueError
#
#    # Log output
#    log_yaml(
#        header="=== RANKED SERVICES ===",
#        level=logging.INFO,
#        logger=logger,
#        ranked_services=ranked_services,
#    )
#    
#
#    # MOVE TO OTHER MODULES & RE-FACTOR
#    #>>>>>>>>>>>>>>>>>>>>>>>>>>>
#    # tes_info_drs will have all the drs costs & info for each TES
#
#    cost_order = sorted(tes_costs.items(), key=lambda x: x[1]["total_costs"])
#    time_order = sorted(tes_task_info.items(), key=lambda x: x[1]["queue_time"]["duration"])
#
#    ranked_services = {uri: 0 for uri, val in cost_order}
#
#    # calculate the final rank on the basis of weight specified by mode
#    for i in range(0, len(cost_order)):
#        ranked_services[cost_order[i][0]] = ranked_services[cost_order[i][0]] + i*mode
#        ranked_services[time_order[i][0]] = ranked_services[time_order[i][0]] + i*(1-mode)
#
#    ranked_services = sorted(ranked_services.items(), key=lambda item: item[1])
#
#    # construct final return object
#    return_array_full = []
#    rank = 1
#    for i in ranked_services:
#        return_dict = {}
#
#        return_dict["access_uris"] = {}
#        return_dict["access_uris"]["tes_uri"] = i[0]
#        for drs_id in drs_object_info.keys():
#            return_dict["access_uris"][drs_id] = tes_info_drs[i[0]][drs_id][0]
#        return_dict["cost_estimate"] = {
#            "amount": tes_info_drs[i[0]]["total_costs"],
#            "currency": tes_info_drs[i[0]]["currency"]
#        }
#        return_dict["time_estimate"] = tes_task_info[i[0]]["queue_time"]
#        return_dict["rank"] = rank
#        return_array_full.extend([return_dict])
#        rank += 1
#
#    # Add warnings
#    response = {"warnings": [], "service_combinations": return_array_full}


# Executed when script is called from command line
if __name__ == "__main__":
    response = rank_services()
    log_yaml(
        header="=== OUTPUT ===",
        level=logging.INFO,
        logger=logger,
        ranking=response,
    )
    # TODO: Do something with response
