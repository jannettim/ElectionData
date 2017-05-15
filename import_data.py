import pandas
from PyQt4 import QtCore, QtGui
from DataTables import DataTable
import sys
import os
import re
import sys
from collections import Counter
from progress.bar import Bar

def concat_sets(election_code, filename=None):
    f_list = os.listdir("data\\harvard_dataverse")
    full_df = None
    count = 0

    bar = Bar('Processing', max=len(f_list))

    for f in f_list:

        # print(f)

        columns = []

        if count >= 20:
            break

        if re.search(r".+\.tab$", f):

            df = pandas.DataFrame.from_csv(os.path.join("data\\harvard_dataverse", f), header=0, sep="\t")
            for col in df.columns.values:
                if re.search(election_code, col):
                    new_col = re.sub(r"(?<=g|s|p|r)\d+(?!$)", "", col)
                    df.rename(columns={col: new_col}, inplace=True)
                    columns.append(new_col)
                elif re.search(r"(?<!_)precinct|precinct_code|state|year|county|parish", col):
                    if col == "parish":
                        df.rename(columns={"parish": "county"}, inplace=True)
                        col = "county"
                    columns.append(col)
                else:
                    pass

            if count == 0:
                full_df = df[columns]
                count += 1
            else:
                full_df = pandas.concat([full_df, df[columns]])
                # count += 1

        bar.next()

    bar.finish()
    full_df.to_csv(filename, sep="\t")
    return full_df

def test_set(filename):
    df = pandas.DataFrame.from_csv(filename, header=0, sep="\t")

    columns = []

    print(df.columns.values)

    for col in df.columns.values:
        if re.search(r"(.*STH.*)|(.*STS.*)|(.*USH.*)|(.*USS.*)|(.*USP.*)|(.*GOV.*)", col):
            new_col = re.sub(r"(?<=g|s|p|r)\d+(?!$)", "", col)
            df.rename(columns={col: new_col}, inplace=True)
            columns.append(new_col)
        elif re.search(r"(?<!_)precinct|precinct_code|state|year|county|parish", col):
            if col == "parish":
                df.rename(columns={"parish": "county"}, inplace=True)
                col = "county"
            columns.append(col)
        else:
            pass

    print(columns)

    # for c in columns:
    #     print(c)
    #     print(df[c].dtype)
    # print(df["g_STH_dv2"])

# test_set("data\\harvard_dataverse\\LA_2000.tab")
# (.*STH.*)|(.*STS.*)|(.*USH.*)|(.*USS.*)|(.*USP.*)|(.*GOV.*)
concat_sets(r".*STH_\wv.*", filename="data\\sth_concatenated.txt")