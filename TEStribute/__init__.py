"""
Exposes TEStribute main function rank_services()
"""
from collections import defaultdict
import logging
import os
from requests.exceptions import MissingSchema
from typing import Dict, List, Union

from drs_client_module import get_available_accessinfo
from tes_client_module import fetch_tasks_info

from TEStribute.compute_costs import sum_costs
from TEStribute.config.parse_config import config_parser, set_defaults
from TEStribute.log.logging_functions import setup_logger
from TEStribute.modes import Mode

# Set up logging
log_file = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "log", "testribute.log")
)
logger = setup_logger("TEStribute", log_file, logging.DEBUG)


def rank_services(
    drs_ids: Union[List, None] = None,
    resource_requirements: Union[Dict, None] = None,
    tes_uris: Union[List, None] = None,
    drs_uris: Union[List, None] = None,
    mode: Union[float, int, Mode, None, str] = None,
    auth_header: Union[None, str] = None,
) -> List:
    """
    Main function that returns a rank-ordered list of GA4GH TES and DRS
    services to use when submitting a TES task to decrease total costs and or
    time. Default values for all parameters are available in and derived from
    the config file `config/config.yaml`, if not provided.
    :param drs_ids: list of DRS identifiers of input files required for the
            task. Can be derived from `inputs` property of the `tesTask`
            model of the GA4GH Task Execution Service schema described here:
            https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution.swagger.yaml
    :param resource_requirements: dictionary of resources required for the
            task; of the form described in the `tesResources` model of the
            _modified_ GA4GH Task Execution Service schema as described here:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
            Note that the `preemptible` and `zones` properties are currently
            not used.
    :param tes_uris: list of root URIs to known TES instances.
    :param drs_uris: list of root URIs to known DRS instances.
    :param mode: either a `mode.Mode` enumeration object, one of its members
            'cost', 'time' or 'random', or one of its values 0, 1, -1,
            respetively. Depending on the mode, services are rank-ordered by
            increasing cost or time, or are randomized for testing/control
            purposes; it is also possible to pass a float between 0 and 1;
            in that case, the value determines the weight between cost (0)
            and time (1) optimization.
    :param auth_header: auth/bearer token to be passed to any TES/DRS calls in
            order to ascertain whether the user has permissions to access
            services specified in `drs_ids`, `tes_instances` and
            `drs_instances`, whether there are particular constraints or
            special provisions in place that apply to the user (e.g., custom
            princes). Currently not implemented.
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
    config = config_parser()

    # Sanitize run mode
    mode = _sanitize_mode(mode=mode)

    # Set defaults if values are missing
    def_values_set = set_defaults(
        defaults=config,
        drs_ids=drs_ids,
        drs_uris=drs_uris,
        mode=mode,
        resource_requirements=resource_requirements,
        tes_uris=tes_uris,
    )
    # pylint: disable=unbalanced-tuple-unpacking
    drs_ids, drs_uris, mode, resource_requirements, tes_uris = def_values_set

    # Ascertain availability of required parameters
    if mode is None:
        logger.error("No valid run mode provided.")
    try:
        cpu_cores = resource_requirements["cpu_cores"]
        ram_gb = resource_requirements["ram_gb"]
        disk_gb = resource_requirements["disk_gb"]
        execution_time_min = resource_requirements["execution_time_min"]
    except KeyError as e:
        logger.error(
            (
                "Required resource parameter missing. Original error "
                "message: {type}: {msg}"
            ).format(type=type(e).__name__, msg=e)
        )
    if not len(tes_uris):
        logger.error("No TES instances available.")
    if len(drs_ids) and not len(drs_uris):
        logger.error("Input files required but no DRS instances available.")

    # Log input parameters
    logger.info("=== INPUT PARAMETERS ===")

    # Log run mode
    logger.info("Run mode:")
    logger.info("- {mode}".format(mode=mode))

    # Log task resources
    logger.info("Requested resources:")
    for name, value in resource_requirements.items():
        logger.info("- {name}: {value}".format(name=name, value=str(value)))

    # Log input file identifiers:
    logger.info("Input file IDs:")
    for drs_id in drs_ids:
        logger.info("- {drs_id}".format(drs_id=drs_id))

    # Log known TES instances
    logger.info("TES instances:")
    for tes in tes_uris:
        logger.info("- {tes}".format(tes=tes))

    # Log known DRS instances
    logger.info("DRS instances:")
    for drs in drs_uris:
        logger.info("- {drs}".format(drs=drs))

    drs_object_info = defaultdict(dict)
    for drs_uri in drs_uris:
        drs_info = get_available_accessinfo(drs_uri, drs_ids)
        for drs_id in drs_info:
            drs_object_info[drs_id].update({drs_uri: drs_info[drs_id]})

    # add a warning for any missing objects
    logger.warning("DRS objects not found at any services: "+str(list(set(drs_ids) - set(drs_object_info.keys()))))

    tes_info = {}
    # Get task queue time and cost estimates from TES instances
    for url in tes_uris:
        try:
            tes_info[url] = fetch_tasks_info(
                url, cpu_cores, ram_gb, disk_gb, execution_time_min
            )
        except MissingSchema:
            logging.error("Service not active " + name + "at" + url)

    # tes_info_drs will have all the drs costs & info for each TES
    tes_info_drs = {}
    for uri, info in tes_info.items():
        tes_info_drs[uri] = sum_costs(
            total_tes_costs=tes_info[uri]["costs_total"],
            data_transfer_rate=info["costs_data_transfer"],
            drs_objects_locations=drs_object_info,
            tes_url=uri
        )

    cost_order = sorted(tes_info_drs.items(), key=lambda x: x[1]["total_costs"])
    time_order = sorted(tes_info.items(), key=lambda x: x[1]["queue_time"]["duration"])

    rank_dict = {uri: 0 for uri, val in cost_order}

    # calculate the final rank on the basis of weight specified by mode
    for i in range(0, len(cost_order)):
        rank_dict[cost_order[i][0]] = rank_dict[cost_order[i][0]] + i*mode
        rank_dict[time_order[i][0]] = rank_dict[time_order[i][0]] + i*(1-mode)

    rank_dict = sorted(rank_dict.items(), key=lambda item: item[1])

    # construct final dict
    return_dict_full = {}
    rank = 1
    for i in rank_dict:
        return_dict = {}
        return_dict["TES"] = i[0]
        for drs_id in drs_object_info.keys():
            return_dict[drs_id] = tes_info_drs[i[0]][drs_id][0]
        return_dict_full.update({rank : return_dict})
        rank += 1
    return return_dict_full


def _sanitize_mode(
    mode: Union[float, int, Mode, None, str] = None
) -> Union[float, None]:
    """
    Validates, sanitizes and returns run mode.

    :param mode: either
            - a `mode.Mode` enumeration member or value
            - one of strings 'cost', 'time' or 'random'
            - one of integers -1, 0, 1
            - a float between 0 and 1
            - None

    :return: sanitized mode which is either of type `mode.Mode`, a float
            between 0 and 1 or `None`. The latter is also returned if an
            invalid value is passed.
    """
    # Check if `None`
    if mode is None:
        logger.warning("Run mode undefined. No mode value passed.")
        return None

    # Check if `Mode` instance
    if isinstance(mode, Mode):
        return float(mode.value)

    # Check if `Mode` key
    if isinstance(mode, str):
        try:
            return float(Mode[mode].value)
        except KeyError:
            logger.warning(
                    "Run mode undefined. Invalid mode value passed: {mode}"
                ).format(mode=mode)
            return None

    # Check if `Mode` value
    if isinstance(mode, int):
        try:
            return float(mode)
        except ValueError:
            logger.warning(
                "Run mode undefined. Invalid mode value passed: {mode}"
            ).format( mode=mode)
            return None

    # Check if allowed float
    if isinstance(mode, float):
        if mode < 0 or mode > 1:
            logger.warning(
                    "Run mode undefined. Out of bounds mode value passed: " "{mode}"
                ).format(mode=mode)
            return None
        else:
            return mode


if __name__ == "__main__":
    response = rank_services()
    logger.debug(response)
