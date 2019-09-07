"""
Exposes TEStribute main function rank_services()
"""
import logging
import os
from typing import Dict, List, Union

from TEStribute.access_drs import fetch_drs_objects_metadata
from TEStribute.access_tes import fetch_tes_task_info
from TEStribute.compute_costs import sum_costs
from TEStribute.config.parse_config import config_parser
from TEStribute.log.logging_functions import log_yaml
from TEStribute.log import setup_logger
from TEStribute.modes import Mode
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

    # CHECK
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # tes_info_drs will have all the drs costs & info for each TES
    tes_info_drs = {}
    for uri, info in tes_task_info.items():
        # TODO : here the older values of each drs object's cost are overwitten
        #  fix the updation, though the normal dicts are NOT overwritten
        tes_info_drs.update({uri: sum_costs(
            total_tes_costs=tes_task_info[uri]["costs_total"],
            data_transfer_rate=info["costs_data_transfer"],
            drs_objects_locations=drs_object_info,
            tes_url=uri)
        })

    cost_order = sorted(tes_info_drs.items(), key=lambda x: x[1]["total_costs"])
    time_order = sorted(tes_task_info.items(), key=lambda x: x[1]["queue_time"]["duration"])

    rank_dict = {uri: 0 for uri, val in cost_order}

    # calculate the final rank on the basis of weight specified by mode
    for i in range(0, len(cost_order)):
        rank_dict[cost_order[i][0]] = rank_dict[cost_order[i][0]] + i*mode
        rank_dict[time_order[i][0]] = rank_dict[time_order[i][0]] + i*(1-mode)

    rank_dict = sorted(rank_dict.items(), key=lambda item: item[1])

    # construct final return object
    return_array_full = []
    rank = 1
    for i in rank_dict:
        return_dict = {}

        return_dict["access_uris"] = {}
        return_dict["access_uris"]["tes_uri"] = i[0]
        for drs_id in drs_object_info.keys():
            return_dict["access_uris"][drs_id] = tes_info_drs[i[0]][drs_id][0]
        return_dict["cost_estimate"] = {
            "amount": tes_info_drs[i[0]]["total_costs"],
            "currency": tes_info_drs[i[0]]["currency"]
        }
        return_dict["time_estimate"] = tes_task_info[i[0]]["queue_time"]
        return_dict["rank"] = rank
        return_array_full.extend([return_dict])
        rank += 1
    return return_array_full
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<


if __name__ == "__main__":
    ranking = rank_services()
    log_yaml(
        header="=== OUTPUT ===",
        level=logging.INFO,
        logger=logger,
        ranking=ranking,
    )
