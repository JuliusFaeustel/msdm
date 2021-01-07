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
datei = open("C:/Users/fried\OneDrive\Desktop\Studium\htw_dresden\studium\Praxissemester/Taktung5.csv","w")
summe = 0
start = time.time()
for n in range(1000000):
    summe = summe+1
i=0

sumTeil_array = []


cursor.execute("SELECT a.TEIL, a.Lagerin, count(b.baseid), (min(unix_timestamp(b.endtime)-unix_timestamp(b.begintime))) AS MinFertigungszeit, (max(unix_timestamp(b.endtime)-unix_timestamp(b.begintime))) AS MaxFertigungszeit, (avg(unix_timestamp(b.endtime)-unix_timestamp(b.begintime))) AS AVGFertigungszeit FROM `basedatain2` as a Join basedata as b on a.baseid=b.baseid WHERE b.endtime IS NOT NULL  AND a.Lagerout > 0  GROUP BY a.lagerin ORDER BY a.TEIL")
result = cursor.fetchall()
connection.commit()
datei.write("TEIL;LAGER;COUNT;MIN;MAX;AVG")
datei.write("\n")
#print(result) 
for fa in result:
    datei.write(str(fa[0])+";"+str(fa[1])+";"+str(fa[2])+";"+str(fa[3])+";"+str(fa[4])+";"+str(fa[5]))
    datei.write("\n")
   # print(str(fa[0])+" "+str(fa[1])+" "+convert_from_s(fa[2])+" "+convert_from_s(fa[3]) +" "+convert_from_s(fa[4]))
    i=i+1

#connection.commit()

ende = time.time()
print('{:5.3f}s'.format(ende-start))
connection.close




