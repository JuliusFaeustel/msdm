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
allLinie = r.smembers("LINIE")
allTeil = r.smembers("TEIL")
allFa = r.smembers("FA")

#Output file vorbereiten
writer = ""
diffFile = open("takt7.csv", "w")
diffFile.write("LINIE;FROM;TO;MIN;MAX;AVG\n")

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

#Iterativ Analyse fuer jede Maschine fahren
for linie in allLinie:
    liSplit = linie.split(":")[1] #fuer Outpur file
    faDict = {}

    #Fuer jeden Fertigungsauftrag
    for fa in allFa:

        #Jede Verknuepfung finden, welche die linie und den fa hat
        r.bitop("AND","opCon",linie,fa)

        #lua Skript ausfuehren und Positionen in der Liste aller Verknuepfungen in result speichern
        result = myLua(keys=['opCon'],args=[1,200])

        #Fuer jede Verknuepfung
        for res in result:

            #Aus allen Verknuepfungen Entsprechende herausholen
            con = allCons[res-1]

            #Anfang, inCounter aus PK herauslesen
            conSplit = con.split(":")
            beginDateStamp = float(conSplit[0])
            inCounter = conSplit[1]
            inData = "in:"+inCounter

            #Jedem entsprechenden fa Anfang, Ende und Teil zuordnen
            if not fa in faDict:
                faDict[fa] = [beginDateStamp,beginDateStamp,r.hget(inData,"TEIL")]

            #Anfang und Ende der Eintraege im faDict auf Rekorde pruefen                
            else:
                oldEarlyBegin = faDict[fa][0]
                oldLateBegin = faDict[fa][1]

                if beginDateStamp < oldEarlyBegin:
                    faDict[fa][0] = beginDateStamp
                
                if beginDateStamp > oldLateBegin:
                    faDict[fa][1] = beginDateStamp

    #faDict nach Anfangsdatum aufsteigend sortieren
    sortedFaDict = dict(sorted(faDict.items(), key=lambda item: item[1][0]))

    #Parameter fuer jede Maschine initial setzen
    notFirst = 0
    minDiff = maxDate.total_seconds()
    maxDiff = zerDiff.total_seconds()
    teilDict = {}

    #Fuer jedes KV-Paar im sortedFaDict
    for el,elList in sortedFaDict.items():
        newTeil = elList[2]

        #Wenn erster fa kann keine Differenz berechnet werden
        if notFirst:
            diffTime = elList[0]  - lastIn

            #String aus *altesTeil*:*neuesTeil*
            teilCon = oldTeil+":"+newTeil

            #Wenn teilCon schon vorhanden
            if teilCon in teilDict:
                minMaxList = teilDict[teilCon]

                #Auf Rekorde pruefen
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
        fromToSplit = k.split(":")
        writer = liSplit+";"+fromToSplit[0]+";"+fromToSplit[1]+";"+str(v[0])+";"+str(v[1])+";"+str(round(v[2]/v[3],2))+"\n"
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