import redis
from datetime import datetime 
import csv
#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
r = redis.Redis(decode_responses=True)

colInd = 0
attributes = ["FA","TEIL","LINIE","LagerIn"]
attributesIndex = [1,3,5,24]
attrIndCounter = 0

#inCounter ist ein Zaehler, der fuer Eindeutigkeit an die In-Datensaetzen (In-DS)
#angehangen wird und deshalb bei Nichtexistens von 1 angefangen gesetzt werden muss
if not r.exists("inCounter"):
    r.set("inCounter","1")
inCounter = r.get("inCounter")

#Manuelle Zuordnung der Spaltennamen
columns = ["DATE","FA","NR","TEIL","SNR","LINIE","E","ScanE","MessageE","A2","V2","A1","V1","UseM3",
	"UseM1","UseM2","Delta","Fehler","Span","ChargeM1","ChargeM2","ChargeM3","ScanA",
	"MessungA","LagerIn","LagerOut","Begin"]

#In-DS schreiben
def writeIn(num,row):
    colInd = 0     
    for dataset in row:
        r.hset("in"+":"+inCounter,columns[colInd],dataset)
        colInd = colInd+1

#Defekte DS (also ohne SNR) schreiben
def writeInDefect(row,inCounter):
    colInd = 0
    for dataset in row:
        r.hset("defect"+":"+"raw"+":"+"in"+":"+inCounter,columns[colInd],dataset)
        colInd = colInd+1        

#Textdatei mit allen In-DS lesen     
with open('allin.txt', 'rt', encoding='utf-16') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    i = 1
    for row in spamreader:
        if not row[4]=='':
            writeIn(i,row)
        
            #Hilfsliste für jede SNR mit offenem (nicht zugeordetem) Output
            #Attribute sind die Input-Keys
            #Nur Inputs mit SNR werden beachtet
            r.rpush(row[4],"in"+":"+inCounter)

            beginDatetime = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S.%f0')
            beginStamp = beginDatetime.timestamp()

            #Liste zur Verknuepfung In und Out bereitstellen
            r.lpush(str(beginStamp)+":"+inCounter+":"+str(beginStamp)+":"+row[4],"in"+":"+inCounter)

            r.rpush("con",str(beginStamp)+":"+inCounter+":"+str(beginStamp)+":"+row[4])

            #In-Out-Verknuepfung in gewuenschte Bitmaps einfuegen
            for attr in attributes:
                r.sadd(attr,attr+":"+row[attributesIndex[attrIndCounter]])
                r.setbit(attr+":"+row[attributesIndex[attrIndCounter]],inCounter,1)
                attrIndCounter = attrIndCounter + 1
            attrIndCounter = 0

            r.lpush(inCounter,beginStamp)
            
            #inCounter setzen
            inCounter = str(int(inCounter)+1)
            r.incr("inCounter")

        else:
            writeInDefect(row,inCounter)
            r.sadd("defect"+":"+"list"+":"+"in","defect"+":"+"raw"+":"+"in"+":"+inCounter)
        
        #Begrenzung der Datensatzanzahl zum testen
        #i=i+1
        #if(i==10000):
            #break
