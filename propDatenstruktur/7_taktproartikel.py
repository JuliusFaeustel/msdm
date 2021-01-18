import pyodbc
import mysql
import mysql.connector
import glob
import csv
from datetime import datetime
import maya
import time

def convert_from_s( seconds ): 
    
    string = str(int(seconds))
    return string
    
def find(l, elem):
    for row, i in enumerate(l):
        try:
            i.index(elem)
        except ValueError:
            continue
        return row
    return -1  
    
def convert_from_datestring( TimeString ): 
    Date = datetime.datetime.strptime(TimeString, "%Y-%m-%dT%H:%M:%S.%f")
    Second = time.mktime(Date.timetuple())
    return Second

connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "", database = "test2")
cursor = connection.cursor()

datei = open("C:/Users/fried\OneDrive\Desktop\Studium\htw_dresden\studium\Praxissemester/Taktung7.csv","w")
datei.write("LINIE;FROM;TO;MIN;MAX;AVG\n")

summe = 0
start = time.time()
for n in range(1000000):
    summe = summe+1
i=0

cursor.execute("Select `LINIE` from basedata group by LINIE ORDER BY linie asc")
linies = cursor.fetchall()
for row in linies:
    print(row[0])
    cursor.execute("SELECT fa, teil, min(unix_timestamp(begintime)), Max(unix_timestamp(begintime)) from basedata WHERE LINIE = '"+row[0]+"' group by FA order by baseid asc")
    fa = cursor.fetchall()
    length = len(fa)
    i = 0
    j = 1
    werte = list()
    while j < length:
        
        
        dauer = fa[j][2]-fa[i][3]
        
        ChangeFromTo = fa[i][1] + fa[j][1] 
        index = find(werte, ChangeFromTo)
        diff = dauer
        if str(diff) >= str(0):
            
            if index == -1:
                   # aktuelle Länge der Ergebnisliste berechnen
                   position = len(werte)

                    # neues Element am Ende der Ergebnisliste einfügen [ChangeFromTo,min,max,avg,count]
                   werte.insert(position, [ChangeFromTo, diff, diff, diff, 1])
            else:
                    # vorhandene Werte aus Liste auslesen
                   minTime = werte[index][1]
                   maxTime = werte[index][2]
                   avgTime = werte[index][3]
                   count = werte[index][4]

                    # Prüfen, ob min/max verändert werden müssen
                   if minTime > diff:
                       werte[index][1] = diff
                   if maxTime < diff:
                       werte[index][2] = diff
                    
                   # Dauer zur AVG Berechnung hinzufügen
                   avgTime = avgTime + diff
                   count = count + 1

                    # Dauer zurück in Liste schreiben
                   werte[index][3] = avgTime
                   werte[index][4] = count    
            i = i+1
            j = j+1
        else:
            break
    werte.sort()   
    for erg in werte:
        #print(erg[3])
        avg = erg[3]/erg[4]
        
        #print(avg)
        datei.write(row[0] +";"+ erg[0][0] +";"+ erg[0][1] +";"+ str(format(erg[1], '.2f')) +";"+ str(format(erg[2], '.2f')) +";"+ str(format(avg, '.2f')) )
        datei.write("\n")
    #print(werte)

connection.commit()

ende = time.time()
print('{:5.3f}s'.format(ende-start))
connection.close




