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
    
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "", database = "test2")
cursor = connection.cursor()
datei = open("C:/Users/fried\OneDrive\Desktop\Studium\htw_dresden\studium\Praxissemester/Taktung2.csv","w")
summe = 0
start = time.time()
for n in range(1000000):
    summe = summe+1
i=0

sumTeil_array = []



cursor.execute("SELECT `TEIL`, COUNT(snrid) AS Anzahl, min(unix_timestamp(endtime) - unix_timestamp(Begintime)) AS MinFertigungszeit, max(unix_timestamp(endtime) - unix_timestamp(Begintime)) AS MaxFertigungszeit, avg(unix_timestamp(endtime) - unix_timestamp(Begintime)) AS AVGFertigungszeit FROM `basedata` WHERE endtime IS NOT NULL  AND (endtime - Begintime)/60 > 0 GROUP BY `TEIL`")

result = cursor.fetchall()
connection.commit()
#print(result) 
for fa in result:
    datei.write(str(fa[0]) +";"+ str(fa[1]) +";"+ str(fa[2]) +";"+ str(fa[3]) +";"+convert_from_s(fa[4]))
    datei.write("\n")
    print(str(fa[0])+" "+str(fa[1])+" "+convert_from_s(fa[2])+" "+convert_from_s(fa[3])+" "+convert_from_s(fa[4]) )
    i=i+1

    
#connection.commit()

ende = time.time()
print('{:5.3f}s'.format(ende-start))
connection.close




