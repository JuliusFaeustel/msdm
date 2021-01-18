import shutil, os
import time
import glob
import projecttest_in as pi
import projecttest_out as po
import pymongo


files_in = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/in/*.txt")
files_out = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/out/*.txt")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]


resp = mydb.in_data_embedded.create_index([ ("SNR", 1) ])
resp = mydb.in_data_embedded.create_index([ ("FA", 1) ])

i=0
while i<len(files_out):
    if i<len(files_in):
        pi.loadInput(files_in[i])
    
    po.loadOutput(files_out[i])
    i+=1
    print(i)
