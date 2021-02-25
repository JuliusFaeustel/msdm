import pymongo
from time import process_time

start = process_time()


myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol = mydb["out_data_embedded"]

# Analyse 5
y = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"LagerIn":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                    {"$project": {"_id":1, "TEIL":1,"LagerIn":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
                                    {'$match': {"SNR": { "$ne": "nan" }}},
                                    {"$group": {"_id":{"LagerIn":"$LagerIn","Teil":"$TEIL"},"anz":{"$sum":1},"min":{"$min": "$difference"}, "max":{"$max": "$difference"}, "avg":{"$avg":"$difference"}}},
                                    {"$sort":{"_id": 1}}])

text_file = open("Analyse_5_Output.txt", "w")
text_file.write("TEIL;LAGER;COUNT;MIN;MAX;AVG\n")
for data in y:
     text_file.write("{};{};{};{};{};{:.2f}\n".format(data.get('_id').get('Teil'),data.get('_id').get('LagerIn'), data.get('anz'), data.get('min')/1000, data.get('max')/1000, data.get('avg')/1000))
text_file.close()

end = process_time()

print(end - start)
