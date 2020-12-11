import redis
from datetime import datetime 
import csv
r = redis.Redis()
colInd = 0
columns = ["DATE","FA","NR","TEIL","SNR","LINIE","E","ScanE","MessageE","A2","V2","A1","V1","UseM3",
	"UseM1","UseM2","Delta","Fehler","Span","ChargeM1","ChargeM2","ChargeM3","ScanA",
	"MessungA","LagerIn","LagerOut","Begin"]
def saveset(num,row):
    colInd = 0     
    for dataset in row:         
        r.hset(row[4]+"."+"in"+"."+row[0],columns[colInd],dataset)
        colInd = colInd+1   
with open('../allin.txt', 'rt', encoding='utf-16') as csvfile:     
    spamreader = csv.reader(csvfile, delimiter=';')     
    i=1    
    for row in spamreader:         
        saveset(i,row)         
        i=i+1
        if(i==10):
            break
