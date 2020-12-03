import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np

import mysql
import mysql.connector
import datetime, time

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor()

def convert_from_s( seconds ): 
    minutes, seconds = divmod(seconds, 60) 
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
    return string

# Teile
teil_array = ["A","B","C","D","E","F","G","H","I","K"]


# Fertigungszeiten
date_min = datetime.datetime.strptime("2100-12-31T23:59:59.000000", "%Y-%m-%dT%H:%M:%S.%f")
second_min = time.mktime(date_min.timetuple())

for Teil in teil_array:
    print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    print("\n")
    print("TEIL: "+ Teil[0])
    print("\n")

    statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.TEIL = '"+Teil[0]+"' AND MA.MerkmalID = 21 GROUP BY Ausprägung ORDER BY Ausprägung"
    cursor.execute(statement)
    LagerIn_List = cursor.fetchall()
    
    for LagerIn in LagerIn_List:
        statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR 	JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.TEIL = '"+Teil[0]+"' AND MA.MerkmalID = 21 AND MA.Ausprägung = '"+LagerIn[0]+"' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
        cursor.execute(statement)
        Anzahl = cursor.fetchone()

        statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.TEIL = '"+Teil[0]+"' AND MA.MerkmalID = 21 AND MA.Ausprägung = '"+LagerIn[0]+"' AND SNR.SNR IS NOT NULL"
        cursor.execute(statement)
        SNRID_List = cursor.fetchall()

        minZeit = second_min
        maxZeit = 0
        avgZeit = 0
        counter = 0

        for SNRID in SNRID_List:
            statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.MerkmalID = 1 AND SNR.ID = "+str(SNRID[0])
            cursor.execute(statement)
            DateIn_result = cursor.fetchone()

            DateIn = datetime.datetime.strptime(DateIn_result[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
            DateIn_second = time.mktime(DateIn.timetuple())

            statement = "SELECT R.ID FROM Rückmeldung R WHERE SNR_ID = "+str(SNRID[0])
            cursor.execute(statement)
            RID_List = cursor.fetchall()

            diff_list = list()

            for RID in RID_List:
                statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID WHERE MA.MerkmalID = 39 AND R.ID = " + str(RID[0])
                cursor.execute(statement)
                DateOut_result = cursor.fetchone()

                DateOut = datetime.datetime.strptime(DateOut_result[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
                DateOut_second = time.mktime(DateOut.timetuple())
                diff = DateOut_second - DateIn_second
                diff_list.append(diff)
            
            diff_list.sort(reverse=True)

            if len(diff_list) != 0:
                if diff_list[0] < minZeit:
                    minZeit = diff_list[0]
                if diff_list[0] > maxZeit:
                    maxZeit = diff_list[0]
                avgZeit = avgZeit + diff_list[0]
            else:
                counter = counter + 1
        
        avgZeit = avgZeit/(len(SNRID_List)-counter)

        print("Ladungsträger: "+LagerIn[0]+"            Anzahl gefertigt: "+str(Anzahl[0])+"            MIN: "+convert_from_s(minZeit)+"            MAX: "+convert_from_s(maxZeit)+"            AVG: "+convert_from_s(avgZeit))



