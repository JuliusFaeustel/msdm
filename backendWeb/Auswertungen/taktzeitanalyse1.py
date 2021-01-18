import redis
import re
from datetime import datetime, timedelta
import time

r = redis.Redis(decode_responses=True)

meanTime = 0
writer=""
allFa = []
for fa in r.scan_iter(match='FA:*', count=300000):
    allFa.append(fa)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = minDateEnd - recDateBeg

allTeil = ["TEIL:A","TEIL:B","TEIL:C","TEIL:D","TEIL:E","TEIL:F","TEIL:G",
          "TEIL:H","TEIL:I","TEIL:J","TEIL:K"]
#allTeil = ["TEIL:A"]
diffFile = open("../AuswertungCSV/takt1.txt", "w")

for teil in allTeil:
    allData = r.lrange(teil, 0, -1)
    diffFile.write(teil + "\n")
    for fa in allFa:
        recDate = zerDiff
        minDate = maxDiff
        avgCounter = 0
        avgTime = 0
        allRejects = 0
        minRejects = 999
        maxRejects = 0
        rejects = 0
        snrDict = {}
        defFa = r.lrange(fa, 0, -1)
        connList = list(set(allData).intersection(defFa))

        if connList:
            for dat in connList:
                connData = r.lrange(dat, 0, -1)
                connOutData = r.lrange(dat, 1, -1)
                localRec = zerDiff
                smallerOneH = 0
                snr = r.hget(connData[0], "SNR")

                if not snr in snrDict:
                    snrDict[snr] = 0

                if len(connData) > 1:
                    beginDate = r.hget(connData[0], "Begin")
                    beginDatetime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')

                    smallerOneH = 0

                    lastRec = recDate

                    for outDat in connOutData:
                        endDate = r.hget(outDat, "Date")
                        endDatetime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')
                        diffTime = endDatetime - beginDatetime

                        if diffTime.total_seconds() <= 3600:
                            smallerOneH = 1
                            if diffTime > recDate:
                                recDate = diffTime
                                snrMax = r.hgetall(outDat)

                            if diffTime > localRec:
                                localRec = diffTime

                        else:
                            smallerOneH = 0
                            recDate = lastRec
                            break

                    if smallerOneH:
                        if localRec < minDate:
                            minDate = localRec
                            snrMin = r.hgetall(connData[0])

                        avgCounter = avgCounter + 1
                        avgTime = avgTime + localRec.total_seconds()

                        snrDict[snr] = snrDict[snr] + 1

                    else:
                        if snrDict[snr] > 0:
                            snrDict[snr] = snrDict[snr] + 1

                else:
                    if snrDict[snr] > 0:
                        snrDict[snr] = snrDict[snr] + 1

            for k, v in snrDict.items():
                rejects = v - 1
                if rejects > maxRejects:
                    maxRejects = rejects

                if rejects < minRejects and rejects >= 0:
                    minRejects = rejects

                if rejects >= 0:
                    allRejects = allRejects + rejects

            if avgCounter > 0:
                #FA ANZAHL MAX-Fert-t MIN-Fert-T Arithmetisches-Mittel
                writer = fa + " " + str(avgCounter) + " " +  str(recDate) + " " + str(minDate) \
                + " " + str((avgTime/avgCounter)/60) + "\n"

                diffFile.write(writer)


