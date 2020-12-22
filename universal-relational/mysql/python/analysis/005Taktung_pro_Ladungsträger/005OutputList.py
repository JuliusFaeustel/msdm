import mysql
import mysql.connector
import datetime, time

for lap in range(10):

    # Verbindung zu DB aufbauen
    connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
    cursor = connection.cursor(buffered=True)

    # Log in DB clearen
    statement = "SET @@profiling = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 10000000;"
    cursor.execute(statement)
    statement = "SET @@profiling = 1"
    cursor.execute(statement)

    # Ausgabeliste definieren
    Result_List = list()

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
        Date = datetime.datetime.strptime(TimeString, "%Y-%m-%dT%H:%M:%S.%f")
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
        
        # Alle LadungsträgerIn für den Teiltyp abfragen
        if actualQuery == 99:
            clear_DB_Log()
        statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.TEIL = '"+ Teil[0] +"' AND M.ID = "+ str(attributeLagerIn[0]) +" GROUP BY Ausprägung ORDER BY Ausprägung"
        cursor.execute(statement)
        actualQuery = actualQuery + 1
        LagerIn_List = cursor.fetchall()
        
        # Alle LadungsträgerIn für den Teiltyp durchlaufen
        for LagerIn in LagerIn_List:

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

            #Variablendeklaration
            minTime = second_min
            maxTime = 0
            avgTime = 0
            counter = 0

            # Alle SNR ID's für Ladungsträger durchlaufen
            for InputID in Input_List:

                # Input-Date für die SNR ID abfragen
                if actualQuery == 99:
                    clear_DB_Log()
                statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE M.ID = "+ str(attributeDateIn[0]) +" AND SNR.ID = "+str(InputID[0])
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                InputDate = cursor.fetchone()

                # InputTime-String in Sekunden umwandeln
                InputDateSecond = convert_from_datestring(InputDate[0][0:-1])

                # Rückmeldungen zur Input ID abfragen
                if actualQuery == 99:
                    clear_DB_Log()
                statement = "SELECT R.ID FROM Rückmeldung R WHERE SNR_ID = "+str(InputID[0])
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                Output_List = cursor.fetchall()

                # Liste der Differenzen deklarieren
                diff_List = list()

                # Alle Rückmeldung ID's durchlaufen
                for OutputID in Output_List:

                    # Output-Date für die Rückmeldung ID abfragen
                    if actualQuery == 99:
                        clear_DB_Log()
                    statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE M.ID = "+ str(attributeDateOut[0]) +" AND R.ID = " + str(OutputID[0])
                    cursor.execute(statement)
                    actualQuery = actualQuery + 1
                    OutputDate = cursor.fetchone()

                    # OutputTime-String in Sekunden umwandeln
                    OutputDateSecond = convert_from_datestring((OutputDate[0][0:-1]))

                    # Differenz berechnen und an Liste anhängen
                    diff = OutputDateSecond - InputDateSecond
                    diff_List.append(diff)
                
                # Differenzliste absteigend sortieren
                diff_List.sort(reverse=True)

                
                if len(diff_List) != 0:
                    # Prüfen, ob Dauer min oder max darstellt
                    if diff_List[0] < minTime:
                        minTime = diff_List[0]
                    if diff_List[0] > maxTime:
                        maxTime = diff_List[0]
                    # Dauer zur AVG Berechnung hinzufügen
                    avgTime = avgTime + diff_List[0]
                # Falls keine Rückmeldung, Anzahl für AVG Berechnung mindern
                else:
                    counter = counter + 1
            
            # AVG-Zeit pro FA in Sekunden
            avgTime = avgTime/(len(Input_List)-counter)

            # Ausgabe pro FA
            index = len(Result_List)
            Result_List.insert(index, [LagerIn[0], AnzahlProLad[0], minTime, maxTime, avgTime])

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

    completeDurationDB = actualDurationDB + DurationDB[0]
    completeQuery = actualQueryDB + QueryCount[0] - 1

    print("Durchlaufzeit DB: "+str(completeDurationDB)+" s")
    print("Queries DB: "+str(completeQuery))
