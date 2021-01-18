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
maxDate = minDateEnd - recDateBeg

#Daten aus Redis laden
allCons = r.lrange("con",0,-1)
allTeil = r.smembers("TEIL")
allLa = r.smembers("LagerIn")

#Output file vorbereiten
writer = ""
diffFile = open("takt5.txt", "w")
diffFile.write("TEIL;LAGER;COUNT;MIN;MAX;AVG\n")

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
    teilSplit = teil.split(":")[1] #fuer Output file

    #Iterativ jeden Ladungstraeger durchgehen
    for lager in allLa:
        laSplit = lager.split(":")[1] #fuer Output file

        #Jede Verknuepfung finden, welche den lager und das teil hat
        r.bitop("AND","opCon",lager,teil)
        
        #lua Skript ausfuehren und Positionen in der Liste aller Verknuepfungen in result speichern
        result = myLua(keys=['opCon'],args=[1,200])

        #Parameter für jeden lager auf initial setzen
        minDiff = maxDate.total_seconds()
        maxDiff = zerDiff.total_seconds()
        allSnr = set()
        avgTime = maxDiff

        #Wenn es Verknuepfung(en) fuer den lager und dieses teil gibt
        if result:

            #Fuer jede Verknuepfung
            for res in result:

                #Aus allen Verknuepfungen Entsprechende herausholen
                con = allCons[res-1]

                #Anfang, Ende und SNR aus PK herauslesen
                conSplit = con.split(":")
                beginDateStamp = float(conSplit[0])
                endDateStamp = float(conSplit[2])
                allSnr.add(conSplit[3])

                #Wenn die Verknuepfung mind. einen Output hat
                if not beginDateStamp == endDateStamp:
                    diffTimeStamp = float(endDateStamp - beginDateStamp)
                    avgTime = avgTime + diffTimeStamp

                    #Auf Rekorde pruefen
                    if diffTimeStamp < minDiff:
                        minDiff = diffTimeStamp

                    if diffTimeStamp > maxDiff:
                        maxDiff = diffTimeStamp

            #writer = lager+";"+str(len(allSnr))+";"+str(maxDiff)+";"+str(minDiff)+";"+str(avgTime/len(allSnr))+"\n"
            writer = teilSplit+";"+laSplit+";"+str(len(allSnr))+";"+str(minDiff)+";"+str(maxDiff)+";"+str(round(avgTime/len(allSnr),2))+"\n"
            diffFile.write(writer)

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


