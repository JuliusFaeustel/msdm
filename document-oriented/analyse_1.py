import pymongo
import pandas as pd
import numpy as np
import glob
import json
import bson
import matplotlib.pyplot as plt
from time import process_time

start = process_time()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol = mydb["out_data_embedded"]

d = mydb.in_data_embedded.distinct("TEIL")

text_file = open("./results/Analyse_1_Output.txt", "w")
text_file.write("TEIL;FA;COUNT;MIN;MAX;AVG;MIN_O;MAX_O;AVG_O\n")
for teil in d:
    x = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                      {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
                                      {'$match': {"difference": {"$lt": 3600000},"SNR": { "$ne": "nan" }, "TEIL": teil}},
                                      {"$group" : {"_id":{"teil":"$TEIL","fa":"$FA"}, "teile_count": {"$sum":1},"maxFert": {"$max": "$difference"},"minFert": {"$min": "$difference"}, "avgFert": {"$avg": "$difference"}}}])

    i = 1
    for data in x:
        avg_t = data.get("avgFert")/1000
        min_t = data.get("minFert")/1000
        max_t = data.get("maxFert")/1000
        fa = data.get("_id").get("fa")
        amount = data.get("teile_count")
        y = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                        {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
                                        {"$match": {"difference": {"$lt": 3600000},"SNR": { "$ne": "nan" },"FA": fa }},
                                        {"$group" : {"_id": {"SNR":"$SNR", "TEIL": "$TEIL", "FA": "$FA"}, "count": {"$sum":1}}},
                                        {"$group": {"_id": {"teil":"$_id.TEIL", "fa":"$_id.FA"},"max_o":{"$max": "$count"},"min_o":{"$min": "$count"},"avg_o":{"$avg": "$count"}}},
                                        {"$sort": {"_id.fa":1}}])
        for values in y:
            teil = values.get("_id").get("teil")
            min_o = values.get("min_o")
            max_o = values.get("max_o")
            avg_o = values.get("avg_o")
    
        text_file.write("{};{};{};{};{};{:.2f};{};{};{:.2f}\n".format(teil, fa, amount, min_t, max_t, avg_t, min_o, max_o, avg_o))
        print(i)
        i += 1

text_file.close()

end = process_time()

print(end-start)