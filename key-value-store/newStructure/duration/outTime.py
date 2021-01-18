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
with open('../../allout.txt', 'rt', encoding='utf-16') as csvfile:     
    spamreader = csv.reader(csvfile, delimiter=';')     
    i=1        
    for row in spamreader:
        
        #writeOut(i,row)
        #recDate = maxDiff
        
        #Zugehörigen Input-SNR-Key finden und aus Liste entfernen
        if r.exists(row[0]):

            writeOut(i,row)
            recDate = maxDiff

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

            dateDatetime = datetime.strptime(row[17], '%Y-%m-%dT%H:%M:%S.%f0')
            dateStamp = dateDatetime.timestamp()
            inDateTime = datetime.strptime(r.hget(conInput,"Begin"), '%Y-%m-%dT%H:%M:%S.%f0')
            inStamp = inDateTime.timestamp()

            inSNR = r.hget(conInput,"SNR")
            
            #Input-Daten finden und Out-DS-Key in Verknuepfung schreiben
            inList = r.lrange(inCounter,0,-1)
            if len(inList) > 1:
                con = str(inStamp)+":"+str(inCounter)+":"+str(inList[1])+":"+str(inSNR)
                if float(dateStamp) > float(inList[1]):
                    newKey = (str(inStamp)+":"+str(inCounter)+":"+str(dateStamp)+":"+str(inSNR))
                    r.rename(con, newKey)
                    con = newKey
                    r.rpop(inCounter)
                    r.rpush(inCounter,dateStamp)
            else:
                con = (str(inStamp)+":"+str(inCounter)+":"+str(inStamp)+":"+str(inSNR))
                newKey = (str(inStamp)+":"+str(inCounter)+":"+str(dateStamp)+":"+str(inSNR))
                #print(con)
                r.rename(con,newKey)
                r.rpush(inCounter,dateStamp)
                con = newKey
                
            inList = r.lrange(inCounter,0,-1)
            #print(inList)
            #getInData = r.hgetall(conInput)
                
            #print(con)
            """
            inTime = con.partition(':'+str(inCounter)+':')[0]
            outTime = con.partition(':'+str(inCounter)+':')[2]
            newKey = con

            if float(dateStamp) > float(outTime):
                newKey = str(inTime)+':'+str(inCounter)+':'+str(dateStamp)
                r.rename(con, newKey)
            """
            
            r.rpush(con,"out"+":"+outCounter)

            r.lset("con",int(inCounter)-1,con)

            #outCounter setzen
            outCounter = str(int(outCounter)+1)
            r.incr("outCounter")
        
            #Begrenzung der Datensatzanzahl zum testen
            #i=i+1
            #if(i==100):
                #break
