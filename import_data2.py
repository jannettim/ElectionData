import requests
from lxml import etree
import csv
import re

def read_results(url):

    html = requests.get(url)
    # print(html.text[:100])
    # soup = BeautifulSoup.soup(html, "html.parser")


    parser = etree.HTMLParser()
    tree = etree.fromstring(html.text, parser=parser)
    table = tree.xpath("/html/body/div/pre")
    count = 0
    test2 = []
    with open("test.csv", "w") as wf:
        for e in table:
            test = e.xpath("//text()")
            if test:
                test2.append(",".join([t for t in test if not re.search(r"((\xa0)|(\r\n)|\.)+", t)]))

        wf.write("\n".join(test2))
read_results("http://www.co.mifflin.pa.us/dept/VoterReg/Pages/EL30.htm")