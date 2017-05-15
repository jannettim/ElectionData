import requests
from lxml import etree
import csv
import urllib.request
import re

def read_results(url):

    """
    Get results from url and parses the html
    :param url: 
    :return: 
    """

    parser = etree.HTMLParser()

    html = urllib.request.urlopen(url)
    tree = etree.parse(html, parser=parser)
    table = tree.xpath("/html/body/div/pre")
    results = []
    row = []
    new_precinct = 0

    with open("test2.csv", "w", newline="") as wf:
        for e in table:
            test = tree.xpath(tree.getpath(e) + "/text()")

            if new_precinct == 1:

                try:
                    if test[0] == "VOTES":
                        pass
                    elif re.search(r"REGISTERED VOTERS \- TOTAL", test[0]):
                        print([re.sub(r"(\s\.)|(?<!\d|\w)|(\xa0)\.", "", t) for t in test if not re.match(r"((\xa0)|(\r\n)|\.)+(?!\w+)|\s+$", t)])
                except IndexError:
                    pass

            try:
                if test[0] == "PRECINCT REPORT":
                    row = []
                    new_precinct = 0

                if re.match(r"\d+\s\w+", test[0]):

                    value = re.split(r"(?<=\d\d\d\d)\s", test[0])
                    row.extend(value)

                    new_precinct = 1

            except IndexError:
                pass

            # row = [re.sub(r"(\s\.)|(?<!\d|\w)|(\xa0)\.", "", t) for t in test if not re.match(r"((\xa0)|(\r\n)|\.)+(?!\w+)|\s+$", t)]
            # results.append(row)

        wr = csv.writer(wf, delimiter=",")
        wr.writerows(results)

read_results("http://www.co.mifflin.pa.us/dept/VoterReg/Pages/EL30.htm")