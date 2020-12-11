import redis
from datetime import datetime 
import csv
#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
r = redis.Redis(decode_responses=True)
colInd = 0

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
recDateMax = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = recDateMax - recDateBeg

#outCounter ist ein Zaehler, der fuer Eindeutigkeit an die Out-Datensaetzen (Out-DS)
#angehangen wird und deshalb bei Nichtexistens von 1 angefangen gesetzt werden muss
if not r.exists("outCounter"):
    r.set("outCounter","1")  
outCounter = r.get("outCounter")

#Manuelle Zuordnung der Spaltennamen
columns = ["SNR","LINIE","TRAEGER","MAT","NAHT","DistMmX","DistMmY","AngleGrad","LengthMM",
           "AngleDiffMM","AngleDiffGrad","AxisDistMMX","AxisDistMMY","AxisDistMM","RTotalNominal",
           "RTotalCurrent","RCount","Date"]

#Out-DS schreiben
def writeOut(num,row):
    colInd = 0     
    for dataset in row:
        r.hset("out"+":"+outCounter,columns[colInd],dataset)
        colInd = colInd+1

#Textdatei mit allen Out-DS lesen     
with open('../allout.txt', 'rt', encoding='utf-16') as csvfile:     
    spamreader = csv.reader(csvfile, delimiter=';')     
    i=1        
    for row in spamreader:     
        writeOut(i,row)
        recDate = maxDiff
        
        #Zugehörigen Input-SNR-Key finden und aus Liste entfernen
        if r.exists(row[0]):

            #Output dem Input mit geringstem Zeitabstand zuordnen
            for inputdat in r.lrange(row[0],0,-1):
                beginDate = r.hget(inputdat,"Begin")
                beginDatetime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')
                endDate = row[17]
                endDatetime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')
                diffTime = endDatetime - beginDatetime
                if diffTime < recDate and diffTime > zerDiff:
                    recDate = diffTime
                    conInput = inputdat

            inCounter = conInput.partition(':')[2]
            #listSNR = r.lpop(row[0])
            #inCounter = listSNR.partition(':')[2]
            
            #Input-Daten finden und Out-DS-Key in Verknuepfung schreiben
            getInData = r.hgetall(conInput)
            r.rpush(getInData.get("SNR")+":"+inCounter,"out"+":"+outCounter)

        #outCounter setzen
        outCounter = str(int(outCounter)+1)
        r.incr("outCounter")

        #Begrenzung der Datensatzanzahl zum testen
        #i=i+1
        #if(i==100):
            #break
