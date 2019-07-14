from tes_client import Client


def fetchTasksInfo(tes_url, cpu_cores, ram_gb, disk_gb, preemtible, zones, execution_time_min):
    c = Client.Client(tes_url)
    response = c.GetTaskInfo(cpu_cores, ram_gb, disk_gb, preemtible, zones, execution_time_min)
    dict_response = response._as_dict()
    return dict_response
