import redis
import re
from datetime import datetime, timedelta
import time

r = redis.Redis(decode_responses=True)

allLa = []
for la in r.scan_iter(match='LagerIn:*', count=300000):
    allLa.append(la)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDate = minDateEnd - recDateBeg
writer = ""
diffFile = open("takt5.txt", "w")
allTeil = ["TEIL:A", "TEIL:B", "TEIL:C", "TEIL:D", "TEIL:E", "TEIL:F", "TEIL:G",
           "TEIL:H", "TEIL:I", "TEIL:J", "TEIL:K"]
# allTeil = ["TEIL:A"]

for teil in allTeil:
    allData = r.lrange(teil, 0, -1)
    diffFile.write(teil + "\n")
    for lager in allLa:
        defLa = r.lrange(lager, 0, -1)
        connList = list(set(allData).intersection(defLa))
        minDiff = maxDate
        maxDiff = zerDiff
        avgTime = zerDiff
        avgCounter = 0

        if connList:
            for con in connList:
                connData = r.lrange(con, 0, -1)
                connOutData = r.lrange(con, 1, -1)

                if connOutData:
                    beginDate = r.hget(connData[0], "Begin")
                    beginDateTime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')

                    outTimeList = []
                    for outDat in connOutData:
                        endDate = r.hget(outDat, "Date")
                        endDateTime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')
                        outTimeList.append(endDateTime)

                    diffTime = max(outTimeList) - beginDateTime

                    avgTime = avgTime + diffTime
                    avgCounter = avgCounter + 1

                    if diffTime < minDiff:
                        minDiff = diffTime

                    if diffTime > maxDiff:
                        maxDiff = diffTime

            writer = lager + ";" + str(maxDiff) + ";" + str(minDiff) + ";" + str(avgTime / avgCounter) + "\n"
            diffFile.write(writer)
