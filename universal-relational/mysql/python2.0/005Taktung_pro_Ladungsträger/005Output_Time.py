import mysql
import mysql.connector
import datetime, time
import pandas as pd
from time import process_time_ns


for lap in range(10):
    start = process_time_ns()

    # Verbindung zu DB aufbauen
    connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
    cursor = connection.cursor(buffered=True)

    # Log in DB clearen
    statement = "SET @@profiling = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 100;"
    cursor.execute(statement)
    statement = "SET @@profiling = 1"
    cursor.execute(statement)

    actualQuery = 0
    actualDurationDB = 0
    actualQueryDB = 0

    def clear_DB_Log ():
        # Prozesszeit auf DB abfragen
        statement = "SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING"
        cursor.execute(statement)
        DurationDB = cursor.fetchone()

        # Anzahl der Queries abfragen
        statement = "SELECT Count(Query_ID) FROM INFORMATION_SCHEMA.PROFILING where State = 'end'"
        cursor.execute(statement)
        QueryCount = cursor.fetchone()

        statement = "SET @@profiling = 0"
        cursor.execute(statement)
        statement = "SET @@profiling_history_size = 0"
        cursor.execute(statement)
        statement = "SET @@profiling_history_size = 100;"
        cursor.execute(statement)
        statement = "SET @@profiling = 1"
        cursor.execute(statement)

        global actualDurationDB
        actualDurationDB = actualDurationDB + DurationDB[0]
        global actualQueryDB
        actualQueryDB = actualQueryDB + QueryCount[0] - 1

        global actualQuery
        actualQuery = 0

        return None

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
    actualQuery = actualQuery + 1
    attributeDateIn = cursor.fetchone()

    # ID des Merkmals DateOut
    statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'DateOut'"
    cursor.execute(statement)
    actualQuery = actualQuery + 1
    attributeDateOut = cursor.fetchone()

    # ID des Merkmals LagerIn
    statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'LagerIn'"
    cursor.execute(statement)
    actualQuery = actualQuery + 1
    attributeLagerIn = cursor.fetchone()

    # Alle Teiltypen abfragen
    statement = "SELECT TEIL FROM TEIL ORDER BY TEIL"
    cursor.execute(statement)
    actualQuery = actualQuery + 1
    Teil_List = cursor.fetchall()

    i = 0
    for Teil in Teil_List:

        # Alle LadungsträgerIn für den Teiltyp abfragen
        if actualQuery == 99:
            clear_DB_Log()
        statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" GROUP BY Ausprägung ORDER BY Ausprägung"
        cursor.execute(statement)
        actualQuery = actualQuery + 1
        LagerIn_List = cursor.fetchall()
        
        # Alle LadungsträgerIn für den Teiltyp durchlaufen
        for LagerIn in LagerIn_List:

            #Variablendeklaration
            minTime = second_min
            maxTime = 0
            avgTime = 0
            counter = 0

            # Anzahl gefertigter Teile pro Ladungsträger des Teiltyps ermitteln
            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND MA.Ausprägung = '"+ LagerIn[0] +"' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            AnzahlProLad = cursor.fetchone()

            # SNR ID's des Teiltypen abrufen, die auf dem aktuellen Ladungsträger gefertigt wurden
            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND MA.Ausprägung = '"+ LagerIn[0] +"' AND SNR.SNR IS NOT NULL"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            Input_List = cursor.fetchall()

            str1 = ''
            for ele in Input_List:  
                str1 = str1 + str(ele[0]) + ','
            str1 = str1[:-1]

            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT SNR.ID, Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.ID IN ("+ str1 +") AND M.ID = "+ str(attributeDateIn[0])
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            InputDates = cursor.fetchall()
            
            InputDates_Frame = pd.DataFrame(InputDates, columns=['ID','DateIn'])
            InputDates_Frame['DateIn'] = InputDates_Frame['DateIn'].apply(convert_from_datestring)
            
            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT R.SNR_ID, MAX(Ausprägung) FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE M.ID = "+ str(attributeDateOut[0]) +" AND R.SNR_ID IN (" + str1 + ") GROUP BY R.SNR_ID"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            OutputDates = cursor.fetchall()

            OutputDates_Frame = pd.DataFrame(OutputDates, columns=['ID','DateOut'])
            OutputDates_Frame['DateOut'] = OutputDates_Frame['DateOut'].apply(convert_from_datestring)

            Frame = pd.merge(InputDates_Frame, OutputDates_Frame, on="ID")

            Frame['diff'] = Frame['DateOut'] - Frame['DateIn']

            minTime = Frame['diff'].min()
            maxTime = Frame['diff'].max()
            avgTime = Frame['diff'].mean()

    if actualQuery != 0:
        statement = "SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING"
        cursor.execute(statement)
        DurationDB = cursor.fetchone()

        # Anzahl der Queries abfragen
        statement = "SELECT Count(Query_ID) FROM INFORMATION_SCHEMA.PROFILING where State = 'end'"
        cursor.execute(statement)
        QueryCount = cursor.fetchone()
    else:
        DurationDB = list()
        DurationDB.append(0)
        QueryCount = list()
        QueryCount.append(0)

    connection.close()

    stop = process_time_ns()
    DurationScript = (stop-start)/10**9
    print("Durchlaufzeit Skript: "+str(DurationScript)+" s")

    completeDurationDB = actualDurationDB + DurationDB[0]
    completeQuery = actualQueryDB + QueryCount[0] - 1

    print("Durchlaufzeit DB: "+str(completeDurationDB)+" s")
    print("Queries DB: "+str(completeQuery))
