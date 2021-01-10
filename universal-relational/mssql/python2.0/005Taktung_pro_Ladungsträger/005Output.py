import matplotlib as mlp
import matplotlib.pyplot as plt

import pyodbc
import datetime, time
import pandas as pd

# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mssql_new/Ergebnisse/005Taktung_pro_Ladungsträger/Taktung_pro_Ladungsträger.txt","w")
dateiCSV = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mssql_new/Ergebnisse/005Taktung_pro_Ladungsträger/Taktung_pro_Ladungsträger.csv","w")

dateiCSV.write("TEIL;LAGER;COUNT;MIN;MAX;AVG\n")

# Flag zur Boxplotzeichnung pro Teiltyp
BoxFlag = False

# Verbindung zu DB aufbauen
server = 'DESKTOP-0IJEV10\\SQLEXPRESS'
database = 'project_3'
username = 'paul'
password = '123'

connection = pyodbc.connect(driver = '{ODBC Driver 17 for SQL Server}', server = server , database = database, UID = username, PWD = password)
cursor = connection.cursor()

# Funktion zur Umwandlung Zeit-String in Sekunden
def convert_from_datestring( TimeString ): 
    Date = datetime.datetime.strptime(TimeString, "%Y-%m-%dT%H:%M:%S.%f0")
    Second = time.mktime(Date.timetuple())
    return Second

# Funktion zur Umwandlung von Sekunden in Zeit-String
def convert_from_s( seconds ): 
    minutes, seconds = divmod(seconds, 60) 
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
    return string

# Maximumwert für minimale Zeit in Sekunden definieren
second_min = convert_from_datestring("2100-12-31T23:59:59.000000")

# ID des Merkmals DateIn
statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'DateIn'"
cursor.execute(statement)
attributeDateIn = cursor.fetchone()

# ID des Merkmals DateOut
statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'DateOut'"
cursor.execute(statement)
attributeDateOut = cursor.fetchone()

# ID des Merkmals LagerIn
statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'LagerIn'"
cursor.execute(statement)
attributeLagerIn = cursor.fetchone()

# Alle Teiltypen abfragen
statement = "SELECT TEIL FROM TEIL ORDER BY TEIL"
cursor.execute(statement)
Teil_List = cursor.fetchall()

i = 0
for Teil in Teil_List:
    datei.write("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    datei.write("\n")
    datei.write("TEIL: "+ Teil[0])
    datei.write("\n")

    if BoxFlag == True:
        BoxAvg_List = list()

    # Alle LadungsträgerIn für den Teiltyp abfragen
    statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" GROUP BY Ausprägung ORDER BY Ausprägung"
    cursor.execute(statement)
    LagerIn_List = cursor.fetchall()
    
    # Alle LadungsträgerIn für den Teiltyp durchlaufen
    for LagerIn in LagerIn_List:

        #Variablendeklaration
        minTime = second_min
        maxTime = 0
        avgTime = 0
        counter = 0

        # Anzahl gefertigter Teile pro Ladungsträger des Teiltyps ermitteln
        statement = "SELECT COUNT(*) FROM (SELECT SNR.SNR FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND MA.Ausprägung = '"+ LagerIn[0] +"' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
        cursor.execute(statement)
        AnzahlProLad = cursor.fetchone()

        # SNR ID's des Teiltypen abrufen, die auf dem aktuellen Ladungsträger gefertigt wurden
        statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND MA.Ausprägung = '"+ LagerIn[0] +"' AND SNR.SNR IS NOT NULL"
        cursor.execute(statement)
        Input_List = cursor.fetchall()

        str1 = ''
        for ele in Input_List:  
            str1 = str1 + str(ele[0]) + ','
        str1 = str1[:-1]

        statement = "SELECT SNR.ID, Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.ID IN ("+ str1 +") AND M.ID = "+ str(attributeDateIn[0])
        cursor.execute(statement)
        InputDates = cursor.fetchall()

        InputDates_Frame = pd.DataFrame.from_records(InputDates, columns = ['ID','DateIn'])
        InputDates_Frame['DateIn'] = InputDates_Frame['DateIn'].apply(convert_from_datestring)

        statement = "SELECT R.SNR_ID, MAX(Ausprägung) FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE M.ID = "+ str(attributeDateOut[0]) +" AND R.SNR_ID IN (" + str1 + ") GROUP BY R.SNR_ID"
        cursor.execute(statement)
        OutputDates = cursor.fetchall()

        OutputDates_Frame = pd.DataFrame.from_records(OutputDates, columns=['ID','DateOut'])
        OutputDates_Frame['DateOut'] = OutputDates_Frame['DateOut'].apply(convert_from_datestring)

        Frame = pd.merge(InputDates_Frame, OutputDates_Frame, on="ID")

        Frame['diff'] = Frame['DateOut'] - Frame['DateIn']

        minTime = Frame['diff'].min()
        maxTime = Frame['diff'].max()
        avgTime = Frame['diff'].mean()

        # Ausgabe pro FA
        datei.write("Ladungsträger: "+LagerIn[0]+"            Anzahl gefertigt: "+str(AnzahlProLad[0])+"            MIN: "+convert_from_s(minTime)+"            MAX: "+convert_from_s(maxTime)+"            AVG: "+convert_from_s(avgTime)+"\n")
        dateiCSV.write(Teil[0] +";"+ LagerIn[0] +";"+ str(AnzahlProLad[0]) +";"+ str(format(minTime, '.2f')) +";"+ str(format(maxTime, '.2f')) +";"+ str(format(avgTime, '.2f')) +"\n")

        if BoxFlag == True:
            BoxAvg_List.append(avgTime/60)

    # Boxplot zeichnen
    if BoxFlag == True:
        plt.figure(1)
        plt.title('Durchschnittliche Taktungen pro Ladungsträger')
        plt.ylabel('Minuten')
        plt.xlabel('Teilart')
        plt.axis
        plt.boxplot(BoxAvg_List, labels=[Teil[0]], showfliers=False, positions=[i+1])
        i = i + 1

if BoxFlag == True:
    plt.savefig('C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/005Taktung_pro_Ladungsträger/boxplots/Average.png')
    plt.close(1)

datei.close()
dateiCSV.close()
connection.close()
