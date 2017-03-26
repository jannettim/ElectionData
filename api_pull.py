"""
Pulls all files from https://dataverse.harvard.edu/dataset.xhtml?persistentId=hdl:1902.1/21919
"""
import requests
import yaml
from zipfile import ZipFile
from io import BytesIO
import os

token = yaml.safe_load(open("tokens.yml"))["token"]

def get_election_ids(version=1.0, write_to_file=True, filename=None):

    ids = []

    if version:
        dataset = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId/versions/{0}?persistentId=hdl:1902.1/21919".format(version))

    else:
        dataset = requests.get(
            "https://dataverse.harvard.edu/api/datasets/:persistentId?persistentId=hdl:1902.1/21919")

    for f in dataset.json()["data"]["files"]:
        ids.append(f["dataFile"]["id"])

    if write_to_file:
        with open(filename, "w") as wf:
            wf.write("\n".join([str(i) for i in ids]))

    return ids

def read_ids(filename):

    with open(filename, "r") as rf:
        ids = rf.read().split("\n")

    return ids

def download_files(ids, path_to_extract):

    file = requests.get("https://dataverse.harvard.edu/api/access/datafiles/{0}?key={1}".format(ids, token), stream=True)
    z = ZipFile(BytesIO(file.content))
    z.extractall(path_to_extract)

def get_metadata(id):

    meta = requests.get("http://dataverse.harvard.edu/api/meta/datafile/{0}?key={1}".format(id, token))
    with open(os.path.join("data\\harvard_dataverse\\metadata", str(id) + ".xml"), "w") as wf:
        wf.write(meta.text)