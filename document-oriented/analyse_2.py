import pymongo
import datetime
from time import process_time

start = process_time()

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekt_simulation"]

mycol = mydb["out_data_embedded"]

x = mydb.in_data_embedded.distinct("TEIL")

liste = []
text_file = open("Analyse_2_Output.txt", "w")
text_file.write("TEIL;COUNT;MIN;MAX;AVG;FAILURE\n")
for teil in x:
    max_val = []
    min_val = []
    avg_val = []
    amount = 0
    z = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "output": {"$arrayElemAt": ["$out", -1]}}},
                                      {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "difference":{'$subtract':['$output.Date','$Begin']}}},
                                      {'$match': {"difference": {"$lt": 3600000},"SNR": { "$ne": "nan" }, "TEIL": teil}},
                                      {"$group" : {"_id":{"teil":"$TEIL","fa":"$FA"}, "teile_count": {"$sum":1}}},
                                      {"$group":{"_id": "$_id.teil", "count": {"$sum":"$teile_count"}}}])
    for value in z:
        total_amount = value.get("count")

    y = mydb.in_data_embedded.aggregate([{"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "out": {"$ifNull": [ "$out", [{"Date":"undefined"}]]}}},
                                            {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "out":{"$arrayElemAt": ["$out", -1]}}},
                                            {"$project": {"_id":1, "TEIL":1,"FA":1, "Begin":1,"SNR":1, "output_date":"$out.Date"}},
                                            {"$match": {"SNR": { "$ne": "nan" },"TEIL": teil}},
                                            {"$sort": {"_id":1}},
                                            {"$group" : {"_id": "$SNR", "count": {"$sum":1},"starts":{"$push":{"Begin":"$Begin","Out":"$output_date"}}}},
                                            {"$match": {"count":{"$gt":1}}}])

    for data in y:
        i = 1
        amount += data.get("count")-1
        differences = []
        data_sorted = sorted(data.get('starts'), key = lambda i: i['Begin'])
        while i < len(data.get('starts')):
            value_1 = data_sorted[i].get('Begin')
            value_2 = data_sorted[i-1].get('Out')
            if(value_2 != 'undefined'):
                value = value_1 - value_2
                if (value > datetime.timedelta()):
                    value = value.total_seconds()
                    differences.append(value)
                    avg_val.append(value)
            i += 1
        if len(differences)>0:
            max_val.append(max(differences))
            min_val.append(min(differences))
    maximum = max(max_val)
    minimum = min(min_val)
    avg = sum(avg_val)/len(avg_val)
    text_file.write("{};{};{};{};{:.2f};{:.2f}\n".format(teil, amount,minimum, maximum, avg, amount/total_amount))
text_file.close()

end = process_time()

print(end - start)
