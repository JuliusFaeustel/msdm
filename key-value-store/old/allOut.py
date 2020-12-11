import redis
from datetime import datetime 
import csv
r = redis.Redis()
colInd = 0
columns = ["SNR","LINIE","TRAEGER","MAT","NAHT","DistMmX","DistMmY","AngleGrad","LengthMM","AngleDiffMM","AngleDiffGrad","AxisDistMMX","AxisDistMMY","AxisDistMM",
	"RTotalNominal","RTotalCurrent","RCount","Date"]
def saveset(num,row):
    colInd = 0     
    for dataset in row:         
        r.hset(row[0]+"."+"out"+"."+row[17],columns[colInd],dataset)
        colInd = colInd+1   
with open('../allout.txt', 'rt', encoding='utf-16') as csvfile:     
    spamreader = csv.reader(csvfile, delimiter=';')     
    i=1    
    for row in spamreader:         
        saveset(i,row)         
        i=i+1
        if(i==10):
            break

