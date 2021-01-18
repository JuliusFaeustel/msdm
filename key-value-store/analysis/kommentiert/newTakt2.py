import redis
from datetime import datetime, timedelta
from time import process_time_ns
import csv

#Timer zur Zeiterfassung starten
start = process_time_ns()

#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert
r = redis.Redis(decode_responses=True)

r.slowlog_reset()

#Beispieldaten, mit denen spaeter kleiner und groeßer verglichen wird
recDateBeg = datetime(1989, 1, 9, 12, 0, 0)
recDateEnd = datetime(1989, 1, 9, 12, 0, 0)
minDateEnd = datetime(2010, 1, 9, 12, 0, 0)
zerDiff = recDateEnd - recDateBeg
maxDiff = minDateEnd - recDateBeg

#Daten aus Redis laden
allCons = r.lrange("con",0,-1)
allConsLen = len(allCons)
allTeil = r.smembers("TEIL")

#Output file vorbereiten
writer = ""
diffFile = open("takt2.txt", "w")
diffFile.write("TEIL;COUNT;MIN;MAX;AVG;FAILURE\n")

#lua-Skript, welches an Redis zur bitweisen Auswertung gegeben wird
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

#lua Skript in Redis einbinden
myLua = r.register_script(lua)

#Iterativ Analyse fuer jedes Teil fahren
for teil in allTeil:
    i=0
    teilSplit = teil.split(":")[1] #fuer Output file

    snrBegDict = {}
    snrEndDict = {}
    allSnr = set()
    maxDate = zerDiff.total_seconds()
    minDate = maxDiff.total_seconds()
    beforeEnd = recDateBeg

    fail = 0
    
    numCounter = 0
    allDiffs = zerDiff.total_seconds()

    #Jede Verknuepfung finden, welche das teil hat
    result = myLua(keys=[teil],args=[1,allConsLen])

    for res in result:
        con = allCons[res-1]
        conSplit = con.split(":")
        beginDateStamp = float(conSplit[0])
        endDateStamp = float(conSplit[2])
        snr = conSplit[3]
        if not snr in snrBegDict:
            snrBegDict[snr] = [beginDateStamp]
            snrEndDict[snr] = [endDateStamp]
        else:
            snrBegDict[snr].append(beginDateStamp)
            snrEndDict[snr].append(endDateStamp)
            
        allSnr.add(snr)

    for snrEl,begList in snrBegDict.items():
        firstCounter = 0        
        timeDict = {}
        beforeEnd = 0
        i = 0
        for beg in begList:
            timeDict[beg] = snrEndDict[snrEl][i]
            i = i + 1
        sortedDict = dict(sorted(timeDict.items(), key=lambda item: item[0]))

        fail = fail + (len(sortedDict)-1)

        if len(sortedDict) > 1:
            for beg,end in sortedDict.items():

                anfang = beg
                ende = end
                
                if firstCounter:
                    diffTime = anfang - beforeEnd
                    if (not beg == end or not beforeEnd == 0):
                        if diffTime < minDate:
                            minDate = diffTime
                        if diffTime > maxDate:
                            maxDate = diffTime

                        numCounter = numCounter + 1
                        allDiffs = allDiffs + diffTime

                beforeEnd = ende
                firstCounter = 1

                if beg == end:
                    firstCounter = 0

    #writer = str(maxDate)+";"+str(minDate)+";"+str(allDiffs/numCounter)+";"+str(fail/len(allSnr))+"\n"
    #writer = str(numCounter)+";"+str(minDate)+";"+str(maxDate)+";"+str(allDiffs/numCounter)+";"+str(fail/len(allSnr))+"\n"
    writer = teilSplit+";"+str(numCounter)+";"+str(minDate)+";"+str(maxDate)+";"+str(round(allDiffs/numCounter,2))+";"+str(round(fail/len(allSnr),4))+"\n"
    diffFile.write(writer)
    
    #print(str(timedelta(seconds=maxDate)))
    #print(maxDate)
    #print(str(timedelta(seconds=minDate)))
    #print(minDate)
    #print(str(timedelta(seconds=(allDiffs/numCounter))))
    #print(str(allDiffs/numCounter))
    #print(str(fail/len(allSnr)))

#Zeiterfassung stoppen und in Konsole ausgeben
stop = process_time_ns()
print(str((stop-start)/10**9))

print(r.slowlog_len())
timeLog = r.slowlog_get(r.slowlog_len())
timeGes = 0
for time in timeLog:
    timeGes = timeGes + time['duration']
r.slowlog_reset()
print(timeGes/10**6)
                     
