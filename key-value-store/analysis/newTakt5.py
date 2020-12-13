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

allTeil = r.smembers("TEIL")
allLa = r.smembers("LagerIn")

writer = ""
diffFile = open("takt5.txt", "w")

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
    diffFile.write(teil + "\n")
    for lager in allLa:
        allSnr = set()
        r.bitop("AND","opCon",lager,teil)
        result = myLua(keys=['opCon'],args=[1,200])
        minDiff = maxDate.total_seconds()
        maxDiff = zerDiff.total_seconds()
        avgTime = maxDiff
        if result:
            for res in result:
                con = allCons[res-1]
                conSplit = con.split(":")
                beginDateStamp = float(conSplit[0])
                endDateStamp = float(conSplit[2])
                allSnr.add(conSplit[3])

                if not beginDateStamp == endDateStamp:
                    diffTimeStamp = float(endDateStamp - beginDateStamp)
                    avgTime = avgTime + diffTimeStamp

                    if diffTimeStamp < minDiff:
                        minDiff = diffTimeStamp
                        #print(minDiff)

                    if diffTimeStamp > maxDiff:
                        maxDiff = diffTimeStamp

            writer = lager+";"+str(len(allSnr))+";"+str(maxDiff)+";"+str(minDiff)+";"+str(avgTime/len(allSnr))+"\n"
            diffFile.write(writer)

stop = process_time_ns()
print("TIME: "+str((stop-start)/10**9))
                



