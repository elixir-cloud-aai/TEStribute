from drs_client import Client


def fetchDataObject(drs_url, object_id):
    c = Client.Client(drs_url)
    response = c.GetObject(object_id)
    response_dict = response._as_dict()
    return response_dict
