import redis
from datetime import datetime, timedelta
from time import process_time_ns
import csv
#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
start = process_time_ns()

r = redis.Redis(decode_responses=True)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDate = minDateEnd - recDateBeg

allCons = r.lrange("con",0,-1)

allLinie = r.smembers("LINIE")
allTeil = r.smembers("TEIL")
allFa = r.smembers("FA")

writer = ""
diffFile = open("takt7.txt", "w")

lua = """
local offset = tonumber(ARGV[1]);
local limit = tonumber(ARGV[2]);
local offset_byte = math.floor(offset / 8);
local ids = {};
local cache = {};

for i = 1, limit do

    if (#ids == limit) then
        break;
    end;

    local pos = redis.call("BITPOS", KEYS[1], 1, offset_byte);

    if (pos == -1) then
        break;
    end;

    cache[pos] = 1;

    if (pos < offset) then
        pos = offset;
    end;

    offset_byte = math.floor(pos / 8) + 1;

    local est;
    local offset_bit = offset_byte * 8 - 1;

    for j = pos, offset_bit do
        if (#ids == limit) then
            break;
        end;
        if (cache[j]) then
            ids[#ids + 1] = j;
        else
            est = redis.call("GETBIT", KEYS[1], j);
            if (est == 1) then
                ids[#ids + 1] = j;
            end;
        end;
    end;

end;

return ids;
"""

myLua = r.register_script(lua)

print("Alles geladen")

for linie in allLinie:
    diffFile.write(linie+"\n")
    faDict = {}
    for fa in allFa:
        r.bitop("AND","opCon",linie,fa)
        result = myLua(keys=['opCon'],args=[1,200])
        for res in result:
            con = allCons[res-1]
            conSplit = con.split(":")
            beginDateStamp = float(conSplit[0])
            inCounter = conSplit[1]
            inData = "in:"+inCounter
            if not fa in faDict:
                faDict[fa] = [beginDateStamp,beginDateStamp,r.hget(inData,"TEIL")]
            else:
                oldEarlyBegin = faDict[fa][0]
                oldLateBegin = faDict[fa][1]

                if beginDateStamp < oldEarlyBegin:
                    faDict[fa][0] = beginDateStamp
                
                if beginDateStamp > oldLateBegin:
                    faDict[fa][1] = beginDateStamp
    sortedFaDict = dict(sorted(faDict.items(), key=lambda item: item[1][0]))
    #print(sortedFaDict)
    notFirst = 0
    minDiff = maxDate.total_seconds()
    maxDiff = zerDiff.total_seconds()
    teilDict = {}
    for el,elList in sortedFaDict.items():
        newTeil = elList[2]
        
        if notFirst:
            diffTime = elList[0]  - lastIn
            teilCon = oldTeil+":"+newTeil
            if teilCon in teilDict:
                minMaxList = teilDict[teilCon]

                if diffTime < minMaxList[0]:
                    minMaxList[0] = diffTime
                if diffTime > minMaxList[1]:
                    minMaxList[1] = diffTime

                minMaxList[2] = minMaxList[2] + diffTime
                minMaxList[3] = minMaxList[3] + 1

                teilDict[teilCon] = minMaxList

            else:
                minMaxList = [diffTime,diffTime,diffTime,1]
                teilDict[teilCon] = minMaxList
        
        oldTeil = newTeil
        lastIn = elList[1]
        notFirst = 1
    
    for k, v in teilDict.items():
        # key max min ges menge
        writer = k +";"+  str(v[1]) + ";" + str(v[0]) + ";" + str(v[2]/v[3])+"\n"
        diffFile.write(writer)

stop = process_time_ns()
print("TIME: "+str((stop-start)/10**9))

#Erstes In vom neuesten FA minus letztes In vom letzten FA
                



