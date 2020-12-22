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

    # Alle LadungsträgerIn abfragen
    statement = "SELECT Ausprägung FROM Merkmalsausprägung WHERE MerkmalID = "+ str(attributeLagerIn[0]) +" ORDER BY Ausprägung"
    cursor.execute(statement)
    LagerIn_List = cursor.fetchall()

    # Variablendeklaration
    Dauer = 0

    # Alle Ladungsträger durchlaufen
    for LagerIn in LagerIn_List:

        # Anzahl gefertigter Teile pro Ladungsträger ermitteln
        if actualQuery == 99:
            clear_DB_Log()
        statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND SNR.SNR IS NOT NULL GROUP BY SNR) Q"
        cursor.execute(statement)
        actualQuery = actualQuery + 1
        AnzahlProLad = cursor.fetchone()

        # SNR ID's abrufen, die auf dem aktuellen Ladungsträger gefertigt wurden
        if actualQuery == 99:
            clear_DB_Log()
        statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND SNR.SNR IS NOT NULL"
        cursor.execute(statement)
        actualQuery = actualQuery + 1
        Input_List = cursor.fetchall()

        # Variablendeklaration
        minInputSecond = second_min
        minInputDate = ''
        maxOutputSecond = 0
        maxOutputDate = ''

        # Alle SNR ID's für Ladungsträger durchlaufen
        for InputID in Input_List:

            # Input-Date für die SNR ID abfragen
            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.ID = "+ str(InputID[0]) +" AND M.ID = "+ str(attributeDateIn[0])
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            InputDate = cursor.fetchone()

            # InputTime-String in Sekunden umwandeln
            InputDateSeconds = convert_from_datestring(InputDate[0][0:-1])

            # Prüfen, ob neues min Input
            if InputDateSeconds < minInputSecond:
                minInputSecond = InputDateSeconds
                minInputDate = InputDate[0]

            # Rückmeldungen zur Input ID abfragen
            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT R.ID FROM Rückmeldung R WHERE R.SNR_ID = "+str(InputID[0])
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            Output_List = cursor.fetchall()

            # Alle Rückmeldung ID's durchlaufen
            for OutputID in Output_List:

                # Output-Date für die Rückmeldung ID abfragen
                if actualQuery == 99:
                    clear_DB_Log()
                statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = R.ID AND o2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE R.ID = "+ str(OutputID[0]) +" AND M.ID = "+ str(attributeDateOut[0])
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                OutputDate = cursor.fetchone()

                # Falls kein Ergebnis, Schleifendurchlauf verlassen
                if not OutputDate:
                    continue
                
                # OutputTime-String in Sekunden umwandeln
                OutputDateSeconds = convert_from_datestring(OutputDate[0][0:-1])

                # Prüfen, ob neues max Output
                if OutputDateSeconds > maxOutputSecond:
                    maxOutputSecond = OutputDateSeconds
                    maxOutputDate = OutputDate[0]
        
        # Differenz zwischen max und min berechnen
        Dauer = maxOutputSecond - minInputSecond

        # Ausgabe
        index = len(Result_List)
        Result_List.insert(index, [LagerIn[0], minInputDate[:19], maxOutputDate[:19], Dauer, AnzahlProLad[0]])

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

        


    