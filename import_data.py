import pandas
from PyQt4 import QtCore, QtGui
from DataTables import DataTable
import sys
import os
import re
import sys
from collections import Counter

f_list = os.listdir("data\\harvard_dataverse")
full_df = None
count = 0
for f in f_list:

    print(f)

    columns = []
    # full_df = None

    # if not f.startswith("AK"):
    #     count = 0
    #     break

    if count >= 20:
        break

    if re.search(r".+\.tab$", f):

        df = pandas.DataFrame.from_csv(os.path.join("data\\harvard_dataverse", f), header=0, sep="\t")
        for col in df.columns.values:
            if re.search(r"(.*STH.*)|(.*STS.*)|(.*USP.*)|(.*GOV.*)", col):
                new_col = re.sub(r"(?<=\w)\d+(?!$)", "", col)
                df.rename(columns={col: new_col}, inplace=True)
                columns.append(new_col)
            elif re.search(r"(?<!_)precinct|precinct_code|state|year|county|parish", col):
                if col == "parish":
                    df.rename(columns={"parish": "county"}, inplace=True)
                columns.append(col)
            else:
                pass

        if count == 0:
            full_df = df[columns]
            count += 1
        else:

            full_df = pandas.concat([full_df, df[columns]])
            count += 1


app = QtGui.QApplication(sys.argv)
datatable = DataTable(full_df, editable=False, window_title="Whole Dataset")
app.exec()