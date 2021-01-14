import redis
from datetime import datetime
from time import process_time_ns
import time

#Timer zur Zeiterfassung starten
start = process_time_ns()

#decode_responses, da die Rueckgabewerte von z.B. r.get(...) sonst als 'binaer' codiert 
r = redis.Redis(decode_responses=True)

r.slowlog_reset()

#Beispieldaten, mit denen spaeter kleiner und groeßer verglichen wird
minDate = datetime(1989, 1, 9, 12, 0, 0)
minDateStamp = minDate.timestamp()
maxDate = datetime(2030, 1, 9, 12, 0, 0)
maxDateStamp = maxDate.timestamp()

#Daten aus Redis laden
allCons = r.lrange("con",0,-1)
allLa = r.smembers("LagerIn")

#Output file vorbereiten
diffFile = open("takt4.txt", "w")
diffFile.write("LAGER;DURATION;START;END;COUNT\n")

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

#Iterativ Analyse fuer jeden Ladungstraeger fahren
for la in allLa:
    laSplit = la.split(":")[1] #fuer Output file

    #lua Skript ausfuehren und Positionen in der Liste aller Verknuepfungen in result speichern
    result = myLua(keys=[la],args=[1,200])

    #Parameter initial setzen
    localMin = maxDateStamp
    localMax = minDateStamp
    snrSet = set()

    #Für jede Verknuepfung mit diesem Ladungstraeger
    for res in result:

        #Entsprechende Verknuepfung holen
        con = allCons[res-1]
        
        conSplit = con.split(":")

        #Anfang, Ende und SNR aus PK herauslesen
        beginDateStamp = float(conSplit[0])
        endDateStamp = float(conSplit[2])
        snrSet.add(conSplit[3])

        #Auf Rekorde pruefen
        if beginDateStamp < localMin:
            localMin = beginDateStamp

        if endDateStamp > localMax:
            localMax = endDateStamp

    #Rekorde zur Ausgabe anpassen
    localMin = datetime.fromtimestamp(localMin)
    localMax = datetime.fromtimestamp(localMax)

    #Differenz ermitteln
    localDiff = localMax - localMin
    
    #writer = la+";"+str(localDiff)+";"+str(localMin)+";"+str(localMax)+";"+str(len(snrSet))+"\n"
    #writer = la+";"+str(localMax)+";"+str(localMin)+";"+str(localDiff)+";"+str(localDiff.total_seconds())+";"+str(len(allData))+"\n"
    writer = laSplit+";"+str(localDiff.total_seconds())+";"+str(localMin)+";"+str(localMax)+";"+str(len(snrSet))+"\n"
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
