"""
Functions that interact with the TES service
"""
from typing import Dict

from tes_client import Client

# TODO: switch to receiving prams as **kwargs if possible
def fetch_tasks_info(
        tes_url: str,
        cpu_cores: int,
        ram_gb: float,
        disk_gb: float,
        execution_time_min: float,
        preemtible=True,
        zones=None
        ) -> Dict:
    """
    :param tes_url: url path of the Task Execution Schema service
    :param cpu_coresFf cores required by the task
    :param ram_gb:  ram in GB for the task
    :param disk_gb: disk space needed by the task in GB
    :param preemtible: True/False for if the task can be run on preemtible
    :param zones: an array of the zones the task can be run on
    :param execution_time_min: time in minutes needed for the execution of the task

    :return: a dict with associated costs & rates (in cases where cost is not computed by TES)
    """
    client = Client.Client(tes_url)
    response = client.GetTaskInfo(
        cpu_cores, ram_gb, disk_gb, preemtible, zones, execution_time_min
    )
    dict_response = response._as_dict()
    return dict_response
