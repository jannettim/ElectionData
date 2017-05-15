import csv
import pandas
import shapefile

#Columns (1,2,3,4,343,344,345) have mixed types.

def remove_non_pres_years():
    df = pandas.read_csv("data\\usp_concatenated.txt", sep="\t", encoding="latin1")

    df2 = df.loc[df.year.isin([1996, 2000, 2004, 2008, 2012])]

    df2.to_csv("data\\usp_concat_selectedyears.txt", sep="\t")

def remove_uss_non_elec_years():

    df = pandas.read_csv("data\\uss_concatenated.txt", sep="\t", encoding="latin1")
    df2 = df.loc[(~df.g_USS_dv.isnull() | ~df.g_USS_iv.isnull() | ~df.g_USS_rv.isnull() | ~df.g_USS_tv.isnull() | ~df.s_USS_dv.isnull() | ~df.s_USS_rv.isnull() | ~df.s_USS_tv.isnull())]
    df2.to_csv("data\\uss_concat_electionyears.txt", sep="\t")

def remove_ush_non_elec_years():

    df = pandas.read_csv("data\\ush_concatenated.txt", sep="\t", encoding="latin1")
    df2 = df.loc[(~df.g_USH_dv2.isnull() | ~df.g_USH_dv3.isnull() | ~df.g_USH_dv4.isnull() | ~df.g_USH_dv5.isnull() |
                   ~df.g_USH_iv.isnull() | ~df.g_USH_rv.isnull() | ~df.g_USH_rv2.isnull() | ~df.g_USH_rv3.isnull() |
                   ~df.g_USH_rv4.isnull() | ~df.g_USH_rv5.isnull() | ~df.g_USH_tv.isnull() | ~df.g_USH_tv1.isnull() |
                   ~df.g_USH_tv2.isnull() | ~df.g_USH_tv3.isnull() | ~df.g_USH_tv4.isnull() | ~df.g_USH_tv5.isnull() |
                   ~df.s_USH_dv.isnull() | ~df.s_USH_rv.isnull() | ~df.s_USH_tv.isnull())]
    df2.to_csv("data\\ush_concat_electionyears.txt", sep="\t")

def remove_sts_non_elect_years():

    df = pandas.read_csv("data\\sts_concatenated.txt", sep="\t", encoding="latin1")
    df2 = df.loc[(~df.g_STS_dv.isnull() | ~df.g_STS_dv1.isnull() | ~df.g_STS_dv10.isnull() | ~df.g_STS_dv11.isnull()
                  | ~df.g_STS_dv12.isnull() | ~df.g_STS_dv13.isnull() | ~df.g_STS_dv14.isnull() | ~df.g_STS_dv2.isnull()
                  | ~df.g_STS_dv3.isnull() | ~df.g_STS_dv4.isnull() | ~df.g_STS_dv5.isnull() | ~df.g_STS_dv6.isnull()
                  | ~df.g_STS_dv7.isnull() | ~df.g_STS_dv8.isnull() | ~df.g_STS_dv9.isnull() | ~df.g_STS_iv.isnull()
                  | ~df.g_STS_rv.isnull() | ~df.g_STS_rv1.isnull() | ~df.g_STS_rv10.isnull() | ~df.g_STS_rv11.isnull()
                  | ~df.g_STS_rv12.isnull() | ~df.g_STS_rv13.isnull() | ~df.g_STS_rv14.isnull() | ~df.g_STS_rv2.isnull()
                  | ~df.g_STS_rv3.isnull() | ~df.g_STS_rv4.isnull() | ~df.g_STS_rv5.isnull() | ~df.g_STS_rv6.isnull()
                  | ~df.g_STS_rv7.isnull() | ~df.g_STS_rv8.isnull() | ~df.g_STS_rv9.isnull() | ~df.g_STS_tv.isnull()
                  | ~df.g_STS_tv1.isnull() | ~df.g_STS_tv10.isnull() | ~df.g_STS_tv11.isnull() | ~df.g_STS_tv12.isnull()
                  | ~df.g_STS_tv13.isnull() | ~df.g_STS_tv14.isnull() | ~df.g_STS_tv2.isnull() | ~df.g_STS_tv3.isnull()
                  | ~df.g_STS_tv4.isnull() | ~df.g_STS_tv5.isnull() | ~df.g_STS_tv6.isnull() | ~df.g_STS_tv7.isnull()
                  | ~df.g_STS_tv8.isnull() | ~df.g_STS_tv9.isnull() | ~df.r_STS_dv.isnull() | ~df.r_STS_dv2.isnull()
                  | ~df.r_STS_rv.isnull() | ~df.r_STS_rv2.isnull() | ~df.r_STS_tv.isnull() | ~df.r_STS_tv2.isnull())]
    df2.to_csv("data\\sts_concat_electionyears.txt", sep="\t")

def remove_sth_non_elect_years():

    df = pandas.read_csv("data\\sth_concatenated.txt", sep="\t", encoding="latin1")
    df2 = df.loc[(~df.g_STH_dv.isnull() | ~df.g_STH_dv1.isnull() | ~df.g_STH_dv10.isnull() | ~df.g_STH_dv11.isnull()
                  | ~df.g_STH_dv12.isnull() | ~df.g_STH_dv13.isnull() | ~df.g_STH_dv14.isnull()
                  | ~df.g_STH_dv15.isnull() | ~df.g_STH_dv16.isnull() | ~df.g_STH_dv2.isnull()
                  | ~df.g_STH_dv3.isnull() | ~df.g_STH_dv4.isnull() | ~df.g_STH_dv5.isnull() | ~df.g_STH_dv6.isnull()
                  | ~df.g_STH_dv7.isnull() | ~df.g_STH_dv8.isnull() | ~df.g_STH_dv9.isnull() | ~df.g_STH_rv.isnull()
                  | ~df.g_STH_rv1.isnull() | ~df.g_STH_rv10.isnull() | ~df.g_STH_rv11.isnull()
                  | ~df.g_STH_rv12.isnull() | ~df.g_STH_rv13.isnull() | ~df.g_STH_rv14.isnull()
                  | ~df.g_STH_rv15.isnull() | ~df.g_STH_rv16.isnull() | ~df.g_STH_rv2.isnull() | ~df.g_STH_rv3.isnull()
                  | ~df.g_STH_rv4.isnull() | ~df.g_STH_rv5.isnull() | ~df.g_STH_rv6.isnull() | ~df.g_STH_rv7.isnull()
                  | ~df.g_STH_rv8.isnull() | ~df.g_STH_rv9.isnull() | ~df.g_STH_tv.isnull() | ~df.g_STH_tv1.isnull()
                  | ~df.g_STH_tv10.isnull() | ~df.g_STH_tv11.isnull() | ~df.g_STH_tv12.isnull()
                  | ~df.g_STH_tv13.isnull() | ~df.g_STH_tv14.isnull() | ~df.g_STH_tv15.isnull()
                  | ~df.g_STH_tv16.isnull() | ~df.g_STH_tv2.isnull() | ~df.g_STH_tv3.isnull() | ~df.g_STH_tv4.isnull()
                  | ~df.g_STH_tv5.isnull() | ~df.g_STH_tv6.isnull() | ~df.g_STH_tv7.isnull() | ~df.g_STH_tv8.isnull()
                  | ~df.g_STH_tv9.isnull() | ~df.r_STH_dv.isnull() | ~df.r_STH_dv2.isnull() | ~df.r_STH_dv3.isnull()
                  | ~df.r_STH_rv.isnull() | ~df.r_STH_rv2.isnull() | ~df.r_STH_rv3.isnull() | ~df.r_STH_tv.isnull()
                  | ~df.r_STH_tv2.isnull() | ~df.r_STH_tv3.isnull() | ~df.s_STH_dv.isnull() | ~df.s_STH_rv.isnull()
                  | ~df.s_STH_tv.isnull() | ~df.sr_STH_dv.isnull() | ~df.sr_STH_rv.isnull() | ~df.sr_STH_tv.isnull())]
    df2.to_csv("data\\sth_concat_electionyears.txt", sep="\t")

def normalize_text(filenames):

    if isinstance(filenames, (list, tuple)):
        for f in filenames:

            df = pandas.DataFrame.from_csv(f, sep="\t", encoding="latin1")

            df.loc[~df.county_name.isnull(), "county"] = df.loc[~df.county_name.isnull()]["county_name"]
            df["county"] = df["county"].str.lower()
            df.drop("county_name", axis=1, inplace=True)
            print(df[["county", "state", "year"]].to_csv("test.csv"))
            break
    else:
        pass

def map_counties_ak():

    sf = shapefile.Reader("D:\\Downloads\\2013-SW-Precinct-Proc-Plan\\SW Proc Shape Files\\2013-SW-PROC-SHAPE-FILES.DBF")
    print(sf.fields)


# normalize_text(["data\\usp_concat_selectedyears.txt", "data\\uss_concat_electionyears.txt"])
map_counties_ak()