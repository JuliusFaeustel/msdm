import redis
import re
from datetime import datetime, timedelta
import time
import plot
r = redis.Redis(decode_responses=True)

minDate = datetime(1989, 1, 9, 12, 0, 0)
maxDate = datetime(2030, 1, 9, 12, 0, 0)
gesDauer = []

allLa = []
for lager in r.scan_iter(match='LagerIn:*',count=300000):
    allLa.append(lager)

for la in allLa:
    allData = r.lrange(la,0,-1)
    localMin = maxDate
    localMax = minDate
    for con in allData:
        conList = r.lrange(con,0,-1)
        conRange = len(conList)
        conBegin = r.hget(conList[0],"Begin")
        conMin = datetime.strptime(conBegin, '%Y-%m-%dT%H:%M:%S.%f0')

        if conMin < localMin:
            localMin = conMin

        if conRange > 1:
            conDate = r.hget(conList[conRange-1],"Date")
            conMax = datetime.strptime(conDate, '%Y-%m-%dT%H:%M:%S.%f0')
            if conMax > localMax:
                localMax = conMax

    localDiff = localMax - localMin

    gesDauer.append(localDiff.total_seconds()/60/60)
    
    if la == 'LagerIn:000027528':
        print("Start: " + str(localMax))
        print("Ende: " + str(localMin))
        print("Dauer: " + str(localDiff))
        print("Dauer: " + str(localDiff.total_seconds()))
        print("Menge: " + str(len(allData)))

plot.boxPlot4(gesDauer) 
