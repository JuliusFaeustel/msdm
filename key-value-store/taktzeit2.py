import redis
import re
from datetime import datetime, timedelta
import time
import plot
r = redis.Redis(decode_responses=True)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = minDateEnd - recDateBeg

plotDict = {}

allTeil = ["TEIL:A","TEIL:B","TEIL:C","TEIL:D","TEIL:E","TEIL:F","TEIL:G",
           "TEIL:H","TEIL:I","TEIL:J","TEIL:K"]
#allTeil = ["TEIL:A"]

def sortListTime(givList):
    myDict = {}
    for el in givList:
        myDict[el] = r.hget(el,"Begin")
    sortedDict = dict(sorted(myDict.items(), key=lambda item: item[1]))
    return sortedDict


for teil in allTeil:
    allData = r.lrange(teil,0,-1)
    snrDict = []
    maxDate = zerDiff
    minDate = maxDiff
    beforeEnd = recDateBeg

    plotList = []
    
    numCounter = 0
    allDiffs = zerDiff
    
    for conDat in allData:
        datList = r.lrange(conDat,0,-1)
        snr = r.hget(datList[0],"SNR")
        if len(r.lrange(snr,0,-1)) > 1 and not snr in snrDict:
            snrDict.append(snr)

    """
    Für jede SNR (SNRs)
        Für jedes Element dieser SNR (Verknüpfungen)
            Datum des ersten Input merken
            Datum des letzten Output merken
            Wenn Differenzen entsprechend sind als Rekorde merken      
    """
    for snrEl in snrDict: #Für jede SNR
        snrElList = r.lrange(snrEl,0,-1)
        firstCounter = 0

        beforeEnd = recDateBeg
        
        sortElList = sortListTime(snrElList)
        
        for inEl in sortElList: #Für jeden Input-DS in SNR (sortiert)
            inCounter = inEl.partition(':')[2]
            datList = r.lrange(snrEl+":"+inCounter,0,-1) #Verknüpfung zum Input
            datRange = len(datList)
            
            if datRange > 1:
            
                beginDate = r.hget(datList[0],"Begin")
                beginDateTime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')
                endDate = r.hget(datList[datRange-1],"Date")
            
                endDateTime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')

                if firstCounter:
                    diffTime = beginDateTime - beforeEnd

                    numCounter = numCounter + 1
                    allDiffs = allDiffs + diffTime
                    plotList.append(diffTime.total_seconds()/60)
                    
                    if diffTime < minDate:
                        minDate = diffTime

                    if diffTime > maxDate:
                        maxDate = diffTime

                beforeEnd = endDateTime
                firstCounter = 1

    if not maxDate == zerDiff:
        print(teil)
        print("Maximum: " + str(maxDate))
        print("Minimum: " + str(minDate))
        print("Durchschnitt: " + str(allDiffs/numCounter))
        print('-----------------')
        plotDict[teil] = plotList

plot.boxPlot(plotDict)
        
