import pandas as pd
import os
import re
from lxml import etree
import requests

def import_ispsr(directory):

    dir_files = [d for d in os.listdir(directory) if re.match(r"DS\d{1,4}", d) and d != "DS0049"]

    df = pd.DataFrame()

    year_lookup = pd.read_excel("data/ICPSR_06311/FolderCode_Year_Lookup.xlsx", "Sheet1")
    year_lookup["Code"] = year_lookup["Code"].astype(str).str.zfill(4)

    state_lookup = pd.read_excel("data/ICPSR_06311/Code_StateLookup.xlsx", "Sheet1")

    for d in dir_files:

        year = year_lookup.loc[year_lookup.Text.str.cat(year_lookup.Code) == d]["Year"].values[0]

        df2 = pd.read_csv(os.path.join(directory, d, os.listdir(os.path.join(directory, d))[0]), sep="\s+",
                         names=["State_Code", "District", "Incumbent", "Republican Votes", "Democratic Votes"])
        df2["Year"] = year

        df = df.append(df2)

    df = pd.merge(df, state_lookup, left_on="State_Code", right_on="Code", how="left")

    return df

def clean_cq_data(datafile, sheet):

    df = pd.read_excel(datafile, sheet, skiprows=4, names=["State_Abbr", "District", "Dem_Can", "Dem_Votes",
                                                           "Dem_Per", "Rep_Can", "Rep_Votes", "Rep_Per",
                                                           "Highest_Minor", "Minor_Votes", "Minor %", "Year"],
                       skip_footer=2)
    df.loc[df.District == "At Large", "District"] = 98

    state_name = pd.read_excel("data\\StateAbbr_Name_Lookup.xlsx", "Sheet1")
    df = pd.merge(df, state_name, how="left", on=["State_Abbr"])

    df.reset_index(inplace=True)
    df.rename(columns={"index": "Election_Id"}, inplace=True)

    print(df)

    1/0

    # print(df.Dem_Votes + df.Rep_Votes + df.Minor_Votes)
    df["Total_Votes"] = df[["Dem_Votes", "Rep_Votes", "Minor_Votes"]].sum(axis=1)
    df["Losing Wasted Votes"] = df["Total_Votes"] - df[["Dem_Votes", "Rep_Votes", "Minor_Votes"]].max(axis=1)

    df["Winning Wasted Votes"] = df[["Dem_Votes", "Rep_Votes", "Minor_Votes"]].max(axis=1) + df["Total_Votes"]/2

    print(df[["Losing Wasted Votes", "Winning Wasted Votes"]])


if __name__ == "__main__":

    # icpsr = import_ispsr("data\\ICPSR_06311")
    clean_cq_data(datafile="data\\CQ Press\\House Elections\\US House Elections By Year By District.xlsx", sheet="Export")