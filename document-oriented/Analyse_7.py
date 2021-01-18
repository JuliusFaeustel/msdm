import pymongo
import pandas as pd
import numpy as np
import glob
import json
import bson
import matplotlib.pyplot as plt
import statistics
import datetime
import time
from time import process_time

start = process_time()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol = mydb["out_data_embedded"]

x = mydb.in_data_embedded.distinct("LINIE")


text_file = open("Analyse_7_Output.txt", "w")
text_file.write("LINIE;FROM;TO;MIN;MAX;AVG\n")
for line in x:
    x = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "LINIE":1,"FA":1, "TEIL":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                        {"$project": {"_id":1, "LINIE":1,"FA":1, "TEIL":1, "Begin":1,"SNR":1, "end":"$output.Date"}},
                                        {"$match": {"SNR": { "$ne": "nan" },"LINIE":line}},
                                        {"$group": {"_id":{"FA": "$FA", "TEIL": "$TEIL"},"start":{"$min": "$Begin"}, "end":{"$max": "$Begin"}}},
                                        {"$sort":{"start": 1}}])

    teil_value = pd.DataFrame()
    i=0
    list = []
    for data in x:
        if i == 0:
            teil_1 = data.get("_id").get('TEIL')
            time_1 = data.get("end")
            i=1
            
        if i==2:
            teil_2 = data.get("_id").get('TEIL')
            time_2 = data.get("start")
            end = data.get("end")
            difference = time_2 - time_1
            seconds = difference.total_seconds()
            if seconds > 0:
                data = {"FROM_TO": teil_1 + " zu " + teil_2, "Dauer": seconds }
                list.append(data)
            else:
                print(teil_1,teil_2)
            teil_1 = teil_2
            time_1 = end
            i=2
        else:
            i += 1
    teil_values = pd.DataFrame(list)
    distinct_values = teil_values["FROM_TO"].unique()
    for value in distinct_values:
        helper_list = teil_values.loc[teil_values['FROM_TO'] == value]["Dauer"]
        maximum = helper_list.max()
        minimum = helper_list.min()
        avg = sum(helper_list)/len(helper_list)
        text_file.write("{};{};{};{};{};{:.2f}\n".format(line,value[0],value[-1],minimum, maximum, avg))
text_file.close()

end = process_time()

print(end - start)