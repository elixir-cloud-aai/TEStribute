"""
exposes the function of TESTribute i.e the task distribution function
"""
import logging

from compute_costs import sum_costs

from distance import return_distance

from drs_client_module import check_data_objects
from tes_client_module import fetch_tasks_info
