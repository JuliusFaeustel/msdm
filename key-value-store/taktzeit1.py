import redis
import re
from datetime import datetime, timedelta
import time
r = redis.Redis(decode_responses=True)

meanTime = 0

allFa = []
for fa in r.scan_iter(match='FA:*'):
    allFa.append(fa)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = minDateEnd - recDateBeg

allTeil = ["TEIL:A","TEIL:B","TEIL:C","TEIL:D","TEIL:E","TEIL:F","TEIL:G",
           "TEIL:H","TEIL:I","TEIL:J","TEIL:K"]
#allTeil = ["TEIL:A"]

for teil in allTeil:
    allData = r.lrange(teil,0,-1)
    print(teil)
    for fa in allFa:
        recDate = zerDiff
        minDate = maxDiff
        avgCounter = 0
        avgTime = 0
        allRejects = 0
        minRejects = 999
        maxRejects = 0
        defFa = r.lrange(fa,0,-1)
        connList = list(set(allData).intersection(defFa))
        
        if connList:
            for dat in connList:
                rejects = 0
                connData = r.lrange(dat,0,-1)
                connOutData = r.lrange(dat,1,-1)
                localRec = zerDiff
                smallerOneH = 0
                
                if len(connData) > 1:              
                    beginDate = r.hget(connData[0],"Begin")
                    beginDatetime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')
                    
                    for outDat in connOutData:
                        smallerOneH = 0
                        endDate = r.hget(outDat,"Date")
                        endDatetime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')
                        diffTime = endDatetime - beginDatetime

                        if diffTime.total_seconds() <= 3600:
                            smallerOneH = 1
                            if diffTime > recDate:
                                recDate = diffTime
                                snrMax = r.hgetall(outDat)

                            if diffTime > localRec:
                                localRec = diffTime
                                
                    if smallerOneH:
                        if localRec < minDate:
                            minDate = localRec
                            snrMin = r.hgetall(connData[0])
                    
                        avgCounter = avgCounter + 1
                        avgTime = avgTime + localRec.total_seconds()

                        rejects = (len(connData) - 2)

                        if rejects > maxRejects:
                            maxRejects = rejects

                        if rejects < minRejects:
                            minRejects = rejects

                allRejects = allRejects + rejects
            
            #print("   " + fa + " | Anzahl Gefertigt: " + str(avgCounter))
            #print("      Max: " + str(recDate) + " " + snrMax.get("SNR")
            #      + " | Min: " + str(minDate) + " " + snrMin.get("SNR"))
            #if avgCounter > 0:
            #    print("         Durchschnitt: " + str((avgTime/avgCounter)/60))
            #print("      Ausschuss gesamt: " + str(allRejects) + " | Max Ausschuss: "
            #      + str(maxRejects) + " | Min Ausschuss: " + str(minRejects))
            #if allRejects > 0:
            #    print("         Durchschnitt: " + str(allRejects/avgCounter))
            #print("-----------------------------------")
