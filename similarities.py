from sklearn.cluster import k_means
import csv
import numpy as np
import pandas as pd

# data = []

# with open("data\\anes_timeseries_cdf\\anes_timeseries_cdf_rawdata.txt", "r") as rf:
#
#     rd = csv.reader(rf, delimiter="|")
#     for row in rd:
#
#         data.append(row)
#
data = pd.read_csv("data\\anes_timeseries_cdf\\anes_timeseries_cdf_rawdata.txt", sep="|", na_values=[" ", ""])

data.dropna(axis=1, inplace=True)
# print(data)
#
# 1/0

X = data.drop("Version", axis=1).values
np.delete(X, np.s_[0:0], axis=1)
kmeans = k_means(X, n_clusters=5)