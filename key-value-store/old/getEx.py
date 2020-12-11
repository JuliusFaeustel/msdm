import redis
import re
from datetime import datetime, timedelta
import time
r = redis.Redis(decode_responses=True)

meanTime = 0

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = minDateEnd - recDateBeg

allTeil = ["TEIL:A","TEIL:B","TEIL:C","TEIL:D","TEIL:E","TEIL:F","TEIL:G",
           "TEIL:H","TEIL:I","TEIL:J","TEIL:K"]

for teil in allTeil:
    recDate = zerDiff
    minDate = maxDiff
    allData = r.lrange(teil,0,-1)
    for dat in allData:
        connData = r.lrange(dat,0,-1)
        connOutData = r.lrange(dat,1,-1)
        if len(connData) > 1:
            
            beginDate = r.hget(connData[0],"Begin")
            beginDatetime = datetime.strptime(beginDate, '%Y-%m-%dT%H:%M:%S.%f0')
            
            for outDat in connOutData:               
                endDate = r.hget(outDat,"Date")
                endDatetime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f0')
                diffTime = endDatetime - beginDatetime
            
                if diffTime > recDate:
                    recDate = diffTime
                    snrMax = r.hgetall(outDat)

                if diffTime < minDate:
                    minDate = diffTime
                    snrMin = r.hgetall(outDat)
        
    print(teil+" : "+str(r.llen(teil))+" gefertigt")
    print(recDate)
    print(snrMax.get("SNR"))
    print(minDate)
    print(snrMin.get("SNR"))
