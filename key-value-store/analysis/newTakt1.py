import redis
from datetime import datetime
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
allConLen = len(allCons)
allTeil = r.smembers("TEIL")
allFa = r.smembers("FA")

#Output file vorbereiten
writer = ""
diffFile = open("takt1.txt", "w")
diffFile.write("TEIL;FA;COUNT;MIN;MAX;AVG\n")

#lua-Skript, welches an Redis zur bitweisen Auswertung gegeben wird
#For license and copyright notice please refer to the last comment in this document
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

    #Iterativ jeden fa durchgehen
    for fa in allFa:
        faSplit = fa.split(":")[1] #fuer Output file

        #Jede Verknuepfung finden, welche den fa und das teil hat
        r.bitop("AND","opCon",teil,fa)

        #lua Skript ausfuehren und Positionen in der Liste aller Verknuepfungen in result speichern
        result = myLua(keys=['opCon'],args=[1,allConLen])

        #Parameter für jeden fa auf initial setzen
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

        #Wenn es Verknuepfung(en) fuer den fa und dieses teil gibt
        if result:

            #Iterativ fuer jede Verknuepfung
            for res in result:

                #Aus allen Verknuepfungen Entsprechende herausholen
                con = allCons[res-1]
                
                localRec = zerDiff
                smallerOneH = 0

                #Anfang, Ende und SNR aus PK herauslesen
                conSplit = con.split(":")
                beginDateStamp = float(conSplit[0])
                endDateStamp = float(conSplit[2])
                snr = conSplit[3]

                #Wenn die Verknuepfung mind. einen Output hat
                if not beginDateStamp == endDateStamp:

                    #Dictionary fuer Gesamtmenge anlegen
                    if not snr in snrDict:
                        snrDict[snr] = 0
                    
                    diffTimeStamp = float(endDateStamp - beginDateStamp)

                    smallerOneH = 0
                    lastRec = maxDiff
    
                    #Nur Dauern <= 1h beachten                  
                    if diffTimeStamp <= 3600:
                        smallerOneH = 1

                        #Auf Rekorde pruefen
                        if diffTimeStamp < minDiff:
                            minDiff = diffTimeStamp

                        if diffTimeStamp > maxDiff:
                            maxDiff = diffTimeStamp

                        avgTime = avgTime + diffTimeStamp
                        avgCounter = avgCounter + 1

                    snrDict[snr] = snrDict[snr] + 1

                #Dictionary fuer Ausschuss anlegen / erweitern
                if not snr in ausDict:
                    ausDict[snr] = 0          
                ausDict[snr] = ausDict[snr] + 1
            
            menge = len(snrDict)

            #Auswertung des Ausschuss
            for k,v in ausDict.items():
                rejects = v - 1
                if rejects > maxRejects:
                    maxRejects = rejects

                if rejects < minRejects and rejects >= 0:
                    minRejects = rejects

                if rejects >= 0:
                    allRejects = allRejects + rejects

            #Division durch 0 vermeiden
            if avgCounter > 0:
                avgGesTime = avgTime/avgCounter
                avgGesReject = allRejects/menge
            else:
                avgGesTime = 0
                avgGesReject = 0
            
            writer = teilSplit+";"+faSplit+";"+str(menge)+";"+str(minDiff)+";"+str(maxDiff)+";"+str(round(avgGesTime,2))+"\n"
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

#Lua Script license and copyright notice
"""

MIT License

Copyright (c) 2017 Alexander Cheprasov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""