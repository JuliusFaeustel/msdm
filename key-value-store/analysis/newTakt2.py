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
	
	#Fuer jede Verknuepfung
    for res in result:
	
		#Aus allen Verknuepfungen Entsprechende herausholen
        con = allCons[res-1]
		
		#Anfang, Ende und SNR aus PK herauslesen
        conSplit = con.split(":")
        beginDateStamp = float(conSplit[0])
        endDateStamp = float(conSplit[2])
        snr = conSplit[3]
		
		#Zeitstempel der richtigen SNR zuordnen
        if not snr in snrBegDict:
            snrBegDict[snr] = [beginDateStamp]
            snrEndDict[snr] = [endDateStamp]
        else:
            snrBegDict[snr].append(beginDateStamp)
            snrEndDict[snr].append(endDateStamp)
            
        allSnr.add(snr)
	
	#Fuer jede SNR mit ihren Zeitstempeln
    for snrEl,begList in snrBegDict.items():
        firstCounter = 0        
        timeDict = {}
        beforeEnd = 0
        i = 0
		
		#Zeitverknuepfungen erstellen (In/Out)
        for beg in begList:
            timeDict[beg] = snrEndDict[snrEl][i]
            i = i + 1
		
		#Zeitverknuepfungen aufsteigend sortieren
        sortedDict = dict(sorted(timeDict.items(), key=lambda item: item[0]))
		
		#Ausschuss berechnen
        fail = fail + (len(sortedDict)-1)
		
		#Wenn mehr als eine Zeitverknuepfung vorhanden (=Ausschuss vorhanden)
        if len(sortedDict) > 1:
			
			#Fuer jede Zeitverknuepfung
            for beg,end in sortedDict.items():

                anfang = beg
                ende = end
                
				#Vorgaengerverknuepfung zur Berechnung vorhanden
                if firstCounter:
                    diffTime = anfang - beforeEnd
					
					#Auf Rekorde pruefen, wenn "ordentliche" Differenz
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

    writer = teilSplit+";"+str(numCounter)+";"+str(minDate)+";"+str(maxDate)+";"+str(round(allDiffs/numCounter,2))+";"+str(round(fail/len(allSnr),4))+"\n"
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