"""
CLI entry point for TEStribute.
"""
import argparse
import json
import logging
import sys

from TEStribute import rank_services

logger = logging.getLogger("TEStribute")
logger.setLevel(logging.INFO)


def main():
    """
    Parse CLI arguments and call `rank_services()` function.
    """
    # Instantiate argument parser
    parser = argparse.ArgumentParser(
        description="""Task distribution for GA4GH TES instances.
        
        Given a list of TES instances and a set of task resource requirements,
        TES instances are ranked by time and/or cost considerations. Optionally,
        the location of input objects can be taken into account."""
    )

    # Create argument groups
    required = parser.add_argument_group("required arguments")

    # Define required arguments
    required.add_argument(
        "--tes-uri",
        action="append",
        help=(
            "URI of known TES instances that the task may be computed on. " \
            "Argument can be specified multiple times."
        ),
        type=str,
        required=True,
        metavar="URI",
    )
    required.add_argument(
        "--cpu-cores",
        help="requested number of CPUs",
        type=int,
        required=True,
        metavar="INT",
    )
    required.add_argument(
        "--ram-gb",
        help="requested RAM required in gigabytes (GB)",
        type=float,
        required=True,
        metavar="FLOAT",
    )
    required.add_argument(
        "--disk-gb",
        help="requested disk size in gigabytes (GB)",
        type=float,
        required=True,
        metavar="FLOAT",
    )
    required.add_argument(
        "--execution-time-sec",
        help="requested execution time in seconds (s)",
        type=int,
        required=True,
        metavar="INT",
    )

    # Define parser arguments
    parser.add_argument(
        "--jwt",
        help="JWT bearer token to be passed on to TES (and DRS) instances",
        type=str,
        default=None,
        metavar="TOKEN",
    )
    parser.add_argument(
        "--object-id",
        action="append",
        help=(
            "DRS ID of object required by the task. Argument can be " \
            "specified multiple times."
        ),
        type=str,
        default=None,
        metavar="ID",
    )
    parser.add_argument(
        "--drs-uri",
        action="append",
        help=(
            "URI of known DRS instance that objects may be read from or " \
            "written to. Required if at least one `--object_id` is " \
            "specified. Argument can be specified multiple times."
        ),
        type=str,
        default=None,
        metavar="URI",
    )
    parser.add_argument(
        "-m", "--mode",
        help=(
            "Mode with which service combinations are ranked. Services can " \
            "be ranked by either 'cost', 'time' or both. For the latter, " \
            "specify a number between 0 and 1, with the boundaries " \
            "representing weights at which services are ranked entirely by " \
            "cost and time, respectively. It is also possible to randomize " \
            "rankings (specify 'random' or -1)."
        ),
        default=0.5,
        metavar="MODE"
    )
    parser.add_argument(
        "-v", "--version",
        action='version',
        version="%(prog)s 0.2.0"
    )
     
    # Parse arguments
    args = parser.parse_args()

    # Process arguments
    if args.object_id is None:
        args.object_id = []
    if args.drs_uri is None:
        args.drs_uri = []
    try:
        args.mode = float(args.mode)
    except ValueError:
        pass

    # Call app's main function with arguments
    try:
        response = rank_services(
            mode=args.mode,
            object_ids=args.object_id,
            drs_uris=args.drs_uri,
            tes_uris=args.tes_uri,
            resource_requirements= {
                "cpu_cores":args.cpu_cores,
                "disk_gb":args.disk_gb,
                "execution_time_sec":args.execution_time_sec,
                "ram_gb":args.ram_gb,
            }
        )
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        sys.exit(1)
    
    # Print output
    sys.stdout.write(json.dumps(response.to_dict()))

if __name__ == "__main__":
    main()
