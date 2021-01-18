import pymongo
import pandas as pd
import numpy as np
import glob
import json
import bson
import matplotlib.pyplot as plt

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekt_simulation"]

mycol = mydb["in_data_embedded"]

x = mydb.system.profile.find({"op": "command"})


text_file = open("Performance_Analyse_7.txt", "w")
summe = 0
for data in x:
    summe += data.get("millis")

text_file.write("{}\n".format(summe))
text_file.close()
