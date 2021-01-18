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

text_file = open("Analyse_Output_find_snr_performance_noindex.txt", "w")
for data in x:
    text_file.write("{}\n".format(data.get("millis")))
text_file.close()
