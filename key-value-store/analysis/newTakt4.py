import redis
from datetime import datetime
from time import process_time_ns
import time
start = process_time_ns()
r = redis.Redis(decode_responses=True)

minDate = datetime(1989, 1, 9, 12, 0, 0)
minDateStamp = minDate.timestamp()
maxDate = datetime(2030, 1, 9, 12, 0, 0)
maxDateStamp = maxDate.timestamp()

allCons = r.lrange("con",0,-1)

allLa = r.smembers("LagerIn")

diffFile = open("takt4.txt", "w")

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

for la in allLa:
    result = myLua(keys=[la],args=[1,200])
    localMin = maxDateStamp
    localMax = minDateStamp
    snrSet = set()
    for res in result:
        con = allCons[res-1]
        conSplit = con.split(":")
        beginDateStamp = float(conSplit[0])
        endDateStamp = float(conSplit[2])
        snrSet.add(conSplit[3])
        
        if beginDateStamp < localMin:
            localMin = beginDateStamp

        if endDateStamp > localMax:
            localMax = endDateStamp

    localMin = datetime.fromtimestamp(localMin)
    localMax = datetime.fromtimestamp(localMax)
    localDiff = localMax - localMin
    
    writer = la+";"+str(localDiff)+";"+str(localMin)+";"+str(localMax)+";"+str(len(snrSet))+"\n"
    #writer = la+";"+str(localMax)+";"+str(localMin)+";"+str(localDiff)+";"+str(localDiff.total_seconds())+";"+str(len(allData))+"\n"
    diffFile.write(writer)

stop = process_time_ns()
print("TIME: "+str((stop-start)/10**9))
