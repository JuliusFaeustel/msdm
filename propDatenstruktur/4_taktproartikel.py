import pyodbc
import mysql
import mysql.connector
import glob
import csv
from datetime import datetime
import maya
import time

def convert_from_s( seconds ): 
    minutes, seconds = divmod(seconds, 60) 
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
    return string
    
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "", database = "test2")
cursor = connection.cursor()
datei = open("C:/Users/fried\OneDrive\Desktop\Studium\htw_dresden\studium\Praxissemester/Taktung4.csv","w")
summe = 0
start = time.time()
for n in range(1000000):
    summe = summe+1
i=0

sumTeil_array = []

cursor.execute("SELECT a.Lagerin, max(unix_timestamp(b.endtime))-MIN(unix_timestamp(a.Begintime)) AS Dauer, min(a.Begintime) AS Start, max(b.endtime) AS Ende, COUNT(b.baseID) FROM basedatain2 AS a JOIN basedata AS b ON a.baseID = b.baseID where a.lagerout > 0 GROUP BY a.Lagerin")
result = cursor.fetchall()
connection.commit()
#print(result) 
datei.write("LAGER;DURATION;START;END;COUNT")
datei.write("\n")
for fa in result:
    datei.write(str(fa[0])+";"+str(fa[1])+";"+str(fa[2])+";"+str(fa[3])+";"+str(fa[4]))
    datei.write("\n")
    #print(str(fa[0])+" "+str(fa[2])+" "+convert_from_s(fa[1])+" "+str(fa[3]) +" "+str(fa[4]))
    i=i+1

    
#connection.commit()

ende = time.time()
print('{:5.3f}s'.format(ende-start))
connection.close




