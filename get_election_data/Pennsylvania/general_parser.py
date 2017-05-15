from PyPDF2 import PdfFileReader
import re

class PrecinctParser:

    def __init__(self, file):

        self.file = file

    def pdf_to_txt(self, output_file=None):

        input1 = PdfFileReader(open(self.file, "rb"))

        num_pages = input1.getNumPages()

        total_text = ""

        for i in range(0, num_pages):

            total_text += input1.getPage(i).extractText()

        if output_file:
            with open(output_file, "w") as wf:
                wf.write(total_text)

        return total_text

    def precinct_parser(self, text):

        precincts = text.split("PRECNINT REPORT")

        precinct_list = []
        elections_list = []
        for p in precincts:

            precinct_list = re.split(r"\s+(?=PRECINCT REPORT)", p)
            #"(\s+|\n)(?=\d{4,}\s\w+)"

        for pre in precinct_list:

            precinct_line = re.search(r"(\d{4,})\s(\w+(\s+|\d+)*)+?", pre)
            precinct_id = precinct_line.group(1)
            precinct_name = precinct_line.group(2)
            elections_list.append((precinct_id, precinct_name, re.split(r"\s+(?=(\s\w+)+(\s*\n|\s+)Vote for\s+\d)", pre)))

        count = 0
        for e in elections_list:
            temp_dict_outer = {}
            for elec in e[2]:
                temp_dict = {}
                # print(elec)
                try:
                    elec_name = re.search(r"((\s\w+)+)(\s*\n|\s+)Vote for\s+\d", elec).group(1)
                    votes = re.findall(r"(((\w+\s)+)|(\w+\-\w+))(\(\w+/*\w*\))*(?:\.*\s+\.)+\s+(\d+)\s*(\d*\.*\d*)", elec)
                    print(votes)
                    # for v in votes:
                    #     temp_dict.update({v[0]: float(v[1])})
                    temp_dict_outer.update({elec_name.strip(): temp_dict})
                except AttributeError:
                    if re.search(r"TOTAL", elec):

                        votes = re.findall(r"(\w*\s*\w+)(?:\s+\-\s+\w+)(?:\.*\s+\.)+\s*(\d+\.*\d*)", elec)
                        for v in votes:
                            temp_dict.update({v[0]: float(v[1])})
                        temp_dict_outer.update({"Total Votes": temp_dict})
                print(temp_dict_outer)
            break

                # count += 1
            # election_type = re.search(r"((\s\w+)+)(\s*\n|\s+)Vote for\s+\d", pre).group(1)
            # print(precinct_id, precinct_name, election_type)
            # re.search(r"(\s*\.\s)+", pre)
            # break


