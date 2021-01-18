import redis
from datetime import datetime
from time import process_time_ns
import csv
start = process_time_ns()
#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
r = redis.Redis(decode_responses=True)

recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDate = minDateEnd - recDateBeg

allCons = r.lrange("con",0,-1)
allConLen = len(allCons)

allTeil = r.smembers("TEIL")
allFa = r.smembers("FA")

writer = ""
diffFile = open("takt1.txt", "w")
diffFile.write("TEIL;FA;COUNT;MIN;MAX;AVG\n")

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

for teil in allTeil:
    teilSplit = teil.split(":")[1]
    for fa in allFa:
        faSplit = fa.split(":")[1]
        r.bitop("AND","opCon",teil,fa)
        result = myLua(keys=['opCon'],args=[1,allConLen])
        minDiff = maxDate.total_seconds()
        maxDiff = zerDiff.total_seconds()
        avgCounter = 0
        avgTime = 0
        allRejects = 0
        minRejects = 999
        maxRejects = 0
        ausCounter = 0
        rejects = 0
        menge = 0
        snrDict = {}
        ausDict = {}
        
        if result:
            for res in result:
                con = allCons[res-1]
                localRec = zerDiff
                smallerOneH = 0
                conSplit = con.split(":")
                beginDateStamp = float(conSplit[0])
                endDateStamp = float(conSplit[2])
                snr = conSplit[3]

                if not beginDateStamp == endDateStamp:

                    if not snr in snrDict:
                        snrDict[snr] = 0
                    
                    diffTimeStamp = float(endDateStamp - beginDateStamp)

                    smallerOneH = 0
                    lastRec = maxDiff

                    if diffTimeStamp <= 3600:
                        smallerOneH = 1
                        if diffTimeStamp < minDiff:
                            minDiff = diffTimeStamp

                        if diffTimeStamp > maxDiff:
                            maxDiff = diffTimeStamp

                        avgTime = avgTime + diffTimeStamp
                        avgCounter = avgCounter + 1

                    snrDict[snr] = snrDict[snr] + 1

                if not snr in ausDict:
                    ausDict[snr] = 0          
                ausDict[snr] = ausDict[snr] + 1
            
            menge = len(snrDict)
            
            for k,v in ausDict.items():
                rejects = v - 1
                if rejects > maxRejects:
                    maxRejects = rejects

                if rejects < minRejects and rejects >= 0:
                    minRejects = rejects

                if rejects >= 0:
                    allRejects = allRejects + rejects

            if avgCounter > 0:
                avgGesTime = avgTime/avgCounter
                avgGesReject = allRejects/menge
            else:
                avgGesTime = 0
                avgGesReject = 0
            
            #writer = teilSplit+";"+faSplit+";"+str(menge)+";"+str(minDiff)+";"+str(maxDiff)+";"+str(avgGesTime)+";"+str(minRejects)+";"+str(maxRejects)+";"+str(avgGesReject)+"\n"
            writer = teilSplit+";"+faSplit+";"+str(menge)+";"+str(minDiff)+";"+str(maxDiff)+";"+str(round(avgGesTime,2))+"\n"
            diffFile.write(writer)

stop = process_time_ns()
print(str((stop-start)/10**9))


