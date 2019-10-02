import argparse

from TEStribute import rank_services

# Define a Argparse instance
parser = argparse.ArgumentParser(description="Receive arguments for the running the TEStribute")

# Create a group for required arguments 
requiredArgument = parser.add_argument_group("required arguments")

# Specify optional arguments
parser.add_argument("-jwt", "--JWT", help="")
parser.add_argument("-m", "--mode",
                     help="Integer or string specifying weight/preferance for cost or time",
                     default=0.5)

# Specify required arguments
requiredArgument.add_argument("-object_ids", "--OBJECT_IDS",
                                nargs="+",
                                help="List of DRS identifiers of input files required for the task",
                                required=True)

requiredArgument.add_argument("-cpu_cores", "--CPU_CORES",
                                help="Requested number of CPUs",
                                type=int,
                                required=True)

requiredArgument.add_argument("-ram_gb", "--RAM_GB",
                                help="Tasks required RAM in gigabytes (GB)",
                                type=int,
                                required=True)

requiredArgument.add_argument("-disk_gb", "--DISK_GB",
                                help="Tasks required disk size in gigabytes (GB)",
                                type=int,
                                required=True)

requiredArgument.add_argument("-execution_time_sec", "--EXECUTION_TIME_SECONDS",
                                help="Tasks required execution in seconds (s)",
                                type=int,
                                required=True)

requiredArgument.add_argument("-tes_uris", "--TES_URIS",
                                nargs="+",
                                help="A list of root URIs to known TES instances.",
                                required=True)

requiredArgument.add_argument("-drs_uris", "--DRS_URIS",
                                nargs="+",    
                                help="A list of root URIs to known DRS instances.",
                                required=True)

# TODO :
#       configure an action send rank_services call
 
# sample reading arguments
arguments = parser.parse_args(["-object_ids","a001","a002",
                               "-drs_uris","http://131.152.229.71/ga4gh/drs/v1/","http://193.166.24.114/ga4gh/drs/v1/",
                               "-tes_uris","http://131.152.229.70/ga4gh/tes/v1/","http://193.166.24.111/ga4gh/tes/v1/",
                               "-cpu_cores","1",
                               "-disk_gb","1",
                               "-execution_time_sec","30",
                               "-ram_gb","1"
                               ])

# sample of rank_servives call
rank_services(mode=arguments.mode,
              object_ids=arguments.OBJECT_IDS,
              drs_uris=arguments.DRS_URIS,
              tes_uris=arguments.TES_URIS,
              resource_requirements= {"cpu_cores":arguments.CPU_CORES,
                                      "disk_gb":arguments.DISK_GB,
                                      "execution_time_sec":arguments.EXECUTION_TIME_SECONDS,
                                      "ram_gb":arguments.RAM_GB,})
