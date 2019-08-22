"""
Exposes TEStribute main function rank_services()
"""
import logging
import os
from typing import Dict, List, Union

from TEStribute import rank_order
from TEStribute.access_drs import fetch_drs_objects_metadata
from TEStribute.access_tes import fetch_tes_task_info
from TEStribute.costs import estimate_costs
from TEStribute.config.parse_config import config_parser
from TEStribute.distances import estimate_distances
from TEStribute.log.logging_functions import log_yaml
from TEStribute.log import setup_logger
from TEStribute.models import Mode
from TEStribute.times import estimate_times
from TEStribute.utils import get_valid_service_combinations
from TEStribute.validate_inputs import validate_input_parameters

# Set up logging
log_file = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "log", "testribute.log")
)
logger = setup_logger("TEStribute", log_file, logging.DEBUG)


def rank_services(
    auth_header: Union[None, str] = None,
    drs_ids: Union[List, None] = None,
    drs_uris: Union[List, None] = None,
    mode: Union[float, int, Mode, None, str] = None,
    resource_requirements: Union[Dict, None] = None,
    tes_uris: Union[List, None] = None,
) -> List:
    """
    Main function that returns a rank-ordered list of GA4GH TES and DRS
    services to use when submitting a TES task to decrease total costs and or
    time. Default values for all parameters are available in and derived from
    the config file `config/config.yaml`, if not provided.

    :param auth_header: Auth/bearer token to be passed to any TES/DRS calls in
            order to ascertain whether the user has permissions to access
            services specified in `drs_ids`, `tes_instances` and
            `drs_instances`, whether there are particular constraints or
            special provisions in place that apply to the user (e.g., custom
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
    # Log user input
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

    # Parse config file
    log_yaml(
        header="=== CONFIG ===",
        level=logging.DEBUG,
        logger=logger,
    )
    config = config_parser()
    log_yaml(
        level=logging.DEBUG,
        logger=logger,
        config=config,
    )

    # Set default values for missing input parameters, validate & sanitize
    log_yaml(
        header="=== VALIDATION ===",
        level=logging.DEBUG,
        logger=logger,
    )
    (
        drs_ids,
        drs_uris,
        mode,
        resource_requirements,
        tes_uris,
    ) = validate_input_parameters(
        defaults=config,
        drs_ids=drs_ids,
        drs_uris=drs_uris,
        mode=mode,
        resource_requirements=resource_requirements,
        tes_uris=tes_uris,
    )

    # Log validated input parameters 
    log_yaml(
        header="=== VALIDATED INPUT PARAMETERS ===",
        level=logging.INFO,
        logger=logger,
        drs_ids=drs_ids,
        drs_uris=drs_uris,
        mode=mode,
        resource_requirements=resource_requirements,
        tes_uris=tes_uris,
    )
    
    # Get metadata for input objects
    if drs_ids is not None:
        try:
            drs_object_info = fetch_drs_objects_metadata(
                drs_uris=drs_uris,
                drs_ids=drs_ids,
                timeout=config["timeout"]
            )
        except Exception:
            logger.critical(
                (
                    "Task cannot be computed: required input file(s) cannot be "
                    "accessed."
                )
            )
            raise

    # Get TES task info for resource requirements
    try:
        tes_task_info = fetch_tes_task_info(
            tes_uris=tes_uris,
            resource_requirements=resource_requirements,
            timeout=config["timeout"]
        )
    except Exception:
        logger.critical(
            (
                "Task cannot be computed: task info could not be obtained."
            )
        )
        raise
    
    # Get valid TES-DRS combinations
    valid_service_combos = get_valid_service_combinations(
        task_info=tes_task_info,
        object_info=drs_object_info,
    )

    # Rank services by costs and/or time
    if Mode["cost"].value <= mode <= Mode["time"].value:
    
        # Compute distances
        tes_object_distances = estimate_distances(
            combinations=valid_service_combos,
        )

        # Compute cost estimates
        if Mode["cost"].value <= mode < Mode["time"].value:
            tes_costs = estimate_costs(
                task_info=tes_task_info,
                object_info=drs_object_info,
                distances=tes_object_distances,
            )
        else: tes_costs = {}

        # Compute time estimates
        if Mode["cost"].value < mode <= Mode["time"].value:
            tes_times = estimate_times(
                task_info=tes_task_info,
                object_info=drs_object_info,
                distances=tes_object_distances,
            )
        else: tes_times = {}

        # Rank by costs/times
        ranked_services = rank_order.cost_time(
            costs=tes_costs,
            times=tes_times,
            weight=mode,
        )

    # Randomize ranks
    elif mode == Mode["random"].value:
        ranked_services = rank_order.randomize(
            uris=tes_uris,
            object_info=drs_object_info,
        )
    
    # Catch other run modes
    else:
        logger.critical(
            (
                "Task cannot be computed: no ranking function defined for "
                "mode: {mode}."
            ).format(mode=mode)
        )
        raise ValueError

    # Log output
    log_yaml(
        header="=== RANKED SERVICES ===",
        level=logging.INFO,
        logger=logger,
        ranked_services=ranked_services,
    )
    

    # MOVE TO OTHER MODULES & RE-FACTOR
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # tes_info_drs will have all the drs costs & info for each TES

    cost_order = sorted(tes_costs.items(), key=lambda x: x[1]["total_costs"])
    time_order = sorted(tes_task_info.items(), key=lambda x: x[1]["queue_time"]["duration"])

    ranked_services = {uri: 0 for uri, val in cost_order}

    # calculate the final rank on the basis of weight specified by mode
    for i in range(0, len(cost_order)):
        ranked_services[cost_order[i][0]] = ranked_services[cost_order[i][0]] + i*mode
        ranked_services[time_order[i][0]] = ranked_services[time_order[i][0]] + i*(1-mode)

    ranked_services = sorted(ranked_services.items(), key=lambda item: item[1])

    # construct final dict
    return_dict_full = {}
    rank = 1
    for i in ranked_services:
        return_dict = {}
        return_dict["TES"] = i[0]
        for drs_id in drs_object_info.keys():
            return_dict[drs_id] = tes_costs[i[0]][drs_id][0]
            return_dict["drs_costs"] = tes_costs[i[0]]["drs_costs"]
            return_dict["total_costs"] = tes_costs[i[0]]["total_costs"]
            return_dict["tes_time"] = tes_task_info[i[0]]["queue_time"]
        return_dict_full.update({rank: return_dict})
        rank += 1
    return return_dict_full
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<


# Executed when script is called from command line
if __name__ == "__main__":
    ranking = rank_services()
    log_yaml(
        header="=== OUTPUT ===",
        level=logging.INFO,
        logger=logger,
        ranking=ranking,
    )
