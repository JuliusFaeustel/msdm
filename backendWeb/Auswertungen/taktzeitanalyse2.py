import redis
import re
from datetime import datetime, timedelta
import time


r = redis.Redis(decode_responses=True)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = minDateEnd - recDateBeg

plotDict = {}

allTeil = ["TEIL:A", "TEIL:B", "TEIL:C", "TEIL:D", "TEIL:E", "TEIL:F", "TEIL:G",
           "TEIL:H", "TEIL:I", "TEIL:J", "TEIL:K"]
diffFile = open("../AuswertungCSV/takt2.txt", "w")
# allTeil = ["TEIL:C"]

def sortListTime(givList):
    myDict = {}
    for el in givList:
        myDict[el] = r.hget(el, "Begin")
    sortedDict = dict(sorted(myDict.items(), key=lambda item: item[1]))
    return sortedDict


for teil in allTeil:
    allData = r.lrange(teil, 0, -1)
    snrDict = []
    allSnr = []
    maxDate = zerDiff
    minDate = maxDiff
    beforeEnd = recDateBeg

    plotList = []

    fail = 0

    numCounter = 0
    allDiffs = zerDiff

    for conDat in allData:
        datList = r.lrange(conDat, 0, -1)
        snr = r.hget(datList[0], "SNR")
        if len(r.lrange(snr, 0, -1)) > 1 and not snr in snrDict:
            snrDict.append(snr)
        if not snr in allSnr:
            allSnr.append(snr)

    """
    Für jede SNR (SNRs)
        Für jedes Element dieser SNR (Verknüpfungen)
            Datum des ersten Input merken
            Datum des letzten Output merken
            Wenn Differenzen entsprechend sind als Rekorde merken      
    """
    for snrEl in snrDict:  # Für jede SNR
        snrElList = r.lrange(snrEl, 0, -1)
        firstCounter = 0

        fail = fail + (len(snrElList) - 1)

        beforeEnd = recDateBeg

        sortElList = sortListTime(snrElList)

        for inEl in sortElList:  # Für jeden Input-DS in SNR (sortiert)
            inCounter = inEl.partition(':')[2]
            datList = r.lrange(snrEl + ":" + inCounter, 0, -1)  # Verknüpfung zum Input
            datRange = len(datList)

            beginDate = r.hget(datList[0], "Begin")
            beginDateTime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')

            if datRange > 1:
                endDate = r.hget(datList[datRange - 1], "Date")
                endDateTime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')

            if firstCounter:
                diffTime = beginDateTime - beforeEnd
                if (datRange > 1 or not beforeEnd == recDateEnd) and diffTime.total_seconds() > 0:

                    numCounter = numCounter + 1
                    allDiffs = allDiffs + diffTime
                    plotList.append(diffTime.total_seconds() / 60)

                    if diffTime < minDate:
                        minDate = diffTime

                    if diffTime > maxDate:
                        maxDate = diffTime

            beforeEnd = endDateTime

            firstCounter = 1

            if not datRange > 1:
                firstCounter = 0

    if not maxDate == zerDiff:
        print(teil)
        writer = teil + " " + str(maxDate) + " " +str(minDate) + " " + str(allDiffs / numCounter) + " " + str(fail / len(allSnr)) +"\n"
        diffFile.write(writer)

