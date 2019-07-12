import tes_client.Client
import drs_client.Client

tes_url = 'http://193.166.24.111/ga4gh/tes/v1/'
drs_url = 'http://193.166.24.114/ga4gh/drs/v1'


def fetchTasksInfo(tes_url, cpu_cores, ram_gb, disk_gb, preemtible, zones, execution_time_min):
    c = tes_client.Client.Client(tes_url)
    return c.GetTaskInfo(cpu_cores, ram_gb, disk_gb, preemtible, zones, execution_time_min)


def fetchDRSInfo(drs_url, object_id):
    drs_client.Client.Client(drs_url)
    c = drs_client.Client.Client(drs_url)
    return c.GetObject(object_id)


if __name__ == "__main__":
    """
    use functions defined
    """
    TesInfo = fetchTasksInfo(tes_url,4,8,10,True,[],20)
    DRS_response = fetchDRSInfo(drs_url, 'a001')

    print(TesInfo)