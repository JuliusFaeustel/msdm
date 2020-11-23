import pymongo
import pandas as pd
import numpy as np
import glob
import json
import bson
import matplotlib.pyplot as plt

def convert_from_ms( milliseconds ): 
	seconds, milliseconds = divmod(milliseconds,1000) 
	minutes, seconds = divmod(seconds, 60) 
	hours, minutes = divmod(minutes, 60) 
	days, hours = divmod(hours, 24) 
	seconds = seconds + milliseconds/1000 
	return days, hours, minutes, seconds

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol = mydb["out_data_embedded"]

x = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                    {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
                                    {'$match': {"difference": {"$lt": 3600000},"SNR": { "$ne": "nan" }}},
                                    {"$group" : {"_id":{"teil":"$TEIL","fa":"$FA"}, "teile_count": {"$sum":1},"maxFert": {"$max": "$difference"},"minFert": {"$min": "$difference"}, "avgFert": {"$avg": "$difference"}}},
                                    {"$group": {"_id":"$_id.teil","fas":{"$push": {"fa":"$_id.fa","count":"$teile_count","maxFert":"$maxFert","minFert":"$minFert", "avgFert":"$avgFert" },},
                                                "count": {"$sum":"$teile_count"}, "maxFert": {"$max":"$maxFert"},"minFert": {"$min":"$minFert"},"avgFert": {"$avg":"$avgFert"}}},
                                    {"$sort":{"_id": 1}}])

i = 1
sum = 0
# while i <= 70:
#     sum = 0
#     y = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
#                                     {"$project": {"_id":1, "TEIL":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
#                                     {'$match': {"difference": {"$gt": i * 3600000,"$lt": (i+1)*3600000},"SNR": { "$ne": "nan" }}},
#                                     {"$group" : {"_id": "$TEIl", "count": {"$sum":1}}}])
#     for data in y:
#         sum += data.get('count')
#     print("{} Stunde: {}".format(i,(sum/4188) * 100))
#     i+=1

teil_lst = []
amount_lst = []
max_lst = []
min_lst = []
avg_lst = []
for data in x:
    print("TEIL: {} Menge: {} MaxFertigungszeit: {} MinFertigungszeit: {} AvgFertigungszeit: {} ".format(data.get('_id'),data.get('count'), convert_from_ms(data.get('maxFert')), convert_from_ms(data.get('minFert')), convert_from_ms(data.get('avgFert'))))
    for data in data.get('fas'):
        print("Fertigungsauftrag: {} Menge: {} MaxFertigungszeit: {} MinFertigungszeit: {} AvgFertigungszeit: {}".format(data.get('fa'),data.get('count'), convert_from_ms(data.get('maxFert')), convert_from_ms(data.get('minFert')), convert_from_ms(data.get('avgFert'))))
    print("\n\n")
#     teil_lst.append(data.get('_id'))
#     amount_lst.append(data.get('count'))
#     max_lst.append(convert_from_ms(data.get('maxFert')))
#     min_lst.append(convert_from_ms(data.get('minFert')))
#     avg_lst.append(convert_from_ms(data.get('avgFert')))
#     print("Teill:", data.get('_id'))
#     print("Anzahl gefertigt:", data.get('count'))
#     print("Maximale Fertigungsdauer: ",convert_from_ms(data.get('maxFert')))
#     print("Minimale Fertigungsdauer:",convert_from_ms(data.get('minFert')) )
#     print("Durschnittliche Fertigungsdauer:",convert_from_ms(data.get('avgFert')) )
#     print("\n")
#     # sum += data.get('count')
#     # print(i)

# print(sum)

x = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                    {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
                                    {"$match": {"difference": {"$lt": 3600000},"SNR": { "$ne": "nan" }}},
                                    {"$group" : {"_id": {"SNR":"$SNR", "TEIL": "$TEIL", "FA": "$FA"}, "count": {"$sum":1}}},
                                    {"$group": {"_id": {"teil":"$_id.TEIL", "fa":"$_id.FA"},"max_o":{"$max": "$count"},"min_o":{"$min": "$count"},"avg_o":{"$avg": "$count"}}},
                                    {"$group": {"_id":"$_id.teil","fas":{"$push": {"fa":"$_id.fa","max_o":"$max_o","min_o":"$min_o","avg_o":"$avg_o" },},
                                            "max": {"$max":"$max_o"},"min": {"$min":"$min_o"},"avg": {"$avg":"$avg_o"}}},
                                    {"$sort":{"_id": 1}}])
    
    
    
for data in x:
    print("TEIL: {} MaxAusschuss: {} MinAusschuss: {} AvgAusschuss: {} ".format(data.get('_id'), data.get('max')-1, data.get('min')-1, data.get('avg')-1))
    for data in data.get('fas'):
        print("Fertigungsauftrag: {} MaxAusschuss: {} MinAusschuss: {} AvgAusschuss: {}".format(data.get('fa'), data.get('max_o')-1, data.get('min_o')-1, data.get('avg_o')-1))
    print("\n\n")

# w = 0.35
# x = np.arange(len(teil_lst))
# plt.figure(figsize=(20,20))
# plot = plt.subplot(211)
# plot.bar(x-0.30,max_lst, width=0.30, color='b', label= "Max")
# plot.bar(x,min_lst, width=0.30, color='g', label= "Min")
# plot.bar(x+0.30,avg_lst, width=0.30, color='r', label="Avg")
# plot.set_ylabel('Zeit in Minuten')
# plot.set_title('MAX, MIN, AVG Fertigungszeiten')
# plot.set_xticks(x)
# plot.set_xticklabels(teil_lst)
# plot.legend()

# plot_amount = plt.subplot(212)
# plot_amount.bar(x,amount_lst, width=0.30, color='b', label= "Menge")
# plot_amount.set_ylabel('Fertigungsmenge')
# plot_amount.set_xlabel('Teil')
# plot_amount.set_title('Fertigungsmenge pro Teil')
# plot_amount.set_xticks(x)
# plot_amount.set_xticklabels(teil_lst)
# plot_amount.legend()

# plt.subplots_adjust(left=0.125,
#                     bottom=0.1, 
#                     right=0.9, 
#                     top=0.9, 
#                     wspace=0.2, 
#                     hspace=0.35)
# plt.show