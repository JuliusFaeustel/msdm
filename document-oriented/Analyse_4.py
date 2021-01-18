import pymongo
import pandas as pd
import numpy as np
import glob
import json
import bson
import matplotlib.pyplot as plt
import statistics
from time import process_time

start = process_time()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekt_simulation"]

mycol = mydb["out_data_embedded"]

# Analyse 4
x = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "LagerIn":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                    {"$project": {"_id":1, "LagerIn":1, "Begin":1,"SNR":1, "end":"$output.Date"}},
                                    {"$match": {"SNR": { "$ne": "nan" }}},
                                    {"$group" : {"_id":{"SNR":"$SNR","LagerIn":"$LagerIn"},"start": {"$min": "$Begin"},"end": {"$max": "$end"}}},
                                    {"$group": {"_id":"$_id.LagerIn","anz":{"$sum":1},"start":{"$min": "$start"}, "end":{"$max": "$end"}}},
                                    {"$project":{"_id":1, "anz":1,"start":1, "end":1, "duration":{'$subtract':['$end','$start']}}},
                                    {"$sort":{"_id": 1}}])

avg = []
text_file = open("./results/Analyse_4_Output.txt", "w")
text_file.write("LAGER;DURATION;START;END;COUNT\n")
for data in x:
    text_file.write("{};{};{};{};{}\n".format(data.get('_id'), data.get('duration')/1000, data.get('start'), data.get('end'), data.get('anz')))
text_file.close()

end = process_time()

print(end - start)