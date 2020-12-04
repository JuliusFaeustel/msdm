import redis
import re
from datetime import datetime, timedelta
import time
r = redis.Redis(decode_responses=True)

minDate = datetime(1989, 1, 9, 12, 0, 0)
maxDate = datetime(2030, 1, 9, 12, 0, 0)
zerDiff = minDate - minDate
maxDiff = maxDate - minDate

#allLi = []
#for li in r.scan_iter(match='LINIE:*',count=300000):
#    allLi.append(li)

diffFile = open("takt7.txt", "w")

allLi = ['LINIE:1','LINIE:2','LINIE:3','LINIE:4','LINIE:5']
#allLi = ['LINIE:3']

#allFa = []
#for fa in r.scan_iter(match='FA:*',count=300000):
#    allFa.append(fa)

def sortFaByBegin(faList):
    myDict = {}
    for fa in faList:
        faName = "FA:"+str(fa)
        conList = r.lrange(faName,0,-1)
        conTi = []
        for con in conList:
            conTi.append(datetime.strptime(r.hget(r.lrange(con,0,-1)[0],"Begin"),'%Y-%m-%dT%H:%M:%S.%f0'))
        myDict[fa] = min(conTi)
    sortedDict = dict(sorted(myDict.items(), key=lambda item: item[1]))
    return sortedDict

for linie in allLi:
    connFaList = []
    allLinieCon = r.lrange(linie,0,-1)
    
    for con in allLinieCon:
        connFaList.append(r.hget(r.lrange(con,0,-1)[0],"FA"))
        
    connFaList = list(set(connFaList))
    sortedFaDict = sortFaByBegin(connFaList) #'009727': datetime.datetime(2018, 12, 18, 10, 22, 41)

    notFirst = 0

    teilDict = {}
    
    recDate = zerDiff
    minDate = maxDiff
    
    for k,v in sortedFaDict.items():
        faName = "FA:"+str(k)
        fa = r.lrange(faName,0,-1)
        outEndList = []
        minMaxList = [] #Max,Min,Ges,Menge
        for con in fa:
            inCon = r.lrange(con,0,-1)
            outList = []
            if len(inCon) > 1:
                outCon = r.lrange(con,1,-1)
                for out in outCon:
                    outDat = datetime.strptime(r.hget(out,"Date"),'%Y-%m-%dT%H:%M:%S.%f0')
                    outList.append(outDat)
                outEndList.append(max(outList))
        endDat = max(outEndList)

        newTeil = r.hget(r.lrange(fa[0],0,-1)[0],"TEIL")
        
        if notFirst:
            diffTime = v - lastEnd
            teilCon = str(lastTeil)+":"+str(newTeil)
            
            if teilCon in teilDict:
                minMaxList = teilDict.get(teilCon)

                if diffTime.total_seconds() > minMaxList[0].total_seconds():
                    minMaxList[0] = diffTime

                if diffTime.total_seconds() < minMaxList[1].total_seconds() and diffTime.total_seconds() > 0:
                    minMaxList[1] = diffTime

                if diffTime.total_seconds() > 0:
                    minMaxList[2] = minMaxList[2] + diffTime                  
                    minMaxList[3] = minMaxList[3] + 1
                    teilDict[teilCon] = minMaxList
                
            else:
                if diffTime.total_seconds() > 0:
                    minMaxList = [diffTime,diffTime,diffTime,1]
                    teilDict[teilCon] = minMaxList
                
        lastTeil = newTeil
        lastEnd = endDat
        notFirst = 1
    
    for k, v in teilDict.items():
        # key max min ges menge
        writer = k +" "+  str(v[0]) + " " + str(v[1]) + " " + str(v[2]/v[3])+"\n"
        diffFile.write(writer)
