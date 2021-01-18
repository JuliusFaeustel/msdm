import mysql
import mysql.connector
import datetime, time
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

    # Alle Teiltypen abfragen
    statement = "SELECT TEIL FROM TEIL ORDER BY TEIL"
    cursor.execute(statement)
    actualQuery = actualQuery + 1
    Teil_List = cursor.fetchall()

    # Alle Teiltypen durchlaufen
    for Teil in Teil_List:

        # FA des Teiltyps abfragen
        if actualQuery == 99:
            clear_DB_Log()
        statement = "SELECT SNR.FA FROM SNR WHERE TEIL = '" + Teil[0] + "' GROUP BY SNR.FA ORDER BY SNR.FA"
        cursor.execute(statement)
        actualQuery = actualQuery + 1
        FA_List = cursor.fetchall()
    
        # Alle FA des Teiltyps durchlaufen
        for FA in FA_List:
            
            # Anzahl gefertigter Teile pro FA ermitteln
            if actualQuery == 99:
                clear_DB_Log() 
            statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            AnzahlProFA = cursor.fetchone()

            # Alle SNR abfragen, die mehr als einen Input in diesem FA haben
            if actualQuery == 99:
                clear_DB_Log() 
            statement = "SELECT SNR.SNR FROM SNR WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(DISTINCT(ID)) > 1"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            Ausschuss_List = cursor.fetchall()

            minFail = 999
            maxFail = 0
            avgFail = 0

            # Alle SNR, die Ausschuss haben, durchlaufen
            for Ausschuss in Ausschuss_List:

                # Anzahl Input DS für SNR finden in diesem FA
                if actualQuery == 99:
                    clear_DB_Log() 
                statement = "SELECT COUNT(*) FROM (SELECT ID FROM SNR WHERE SNR.SNR ='" + Ausschuss[0] + "' AND FA = '" + FA[0] +"') Q"
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                AnzahlFail = cursor.fetchone()

                # Ausschuss ist alles mehr als ein Input 
                AnzahlFail = int(AnzahlFail[0])-1

                # Prüfen, ob Ausschuss min oder max darstellt
                if AnzahlFail < minFail:
                    minFail = AnzahlFail
                if AnzahlFail > maxFail:
                    maxFail = AnzahlFail
                
                # Ausschuss zur AVG-Berechnung hinzufügen
                avgFail = avgFail + AnzahlFail
            

            # Prüfen, ob minFail noch initial ist und ggfls. auf 0 setzen
            if minFail == 999:
                minFail = 0

            # Alle Input ID's abfragen, die einen Output haben, zum FA gehören und SNR != NULL
            if actualQuery == 99:
                clear_DB_Log() 
            statement = "SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.ID"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            SNRID_List = cursor.fetchall()

            # Variablendeklaration pro FA
            minTime = second_min
            maxTime = 0
            avgTime = 0
            avgDifference = 0
            
            # Alle ID's durchlaufen
            for SNRID in SNRID_List:

                # Listdeklaration, in der Dauern (Input DS bis zugehörigem letztem Output DS) einer SNR gespeichert werden
                help_List = list()

                # Input-Zeit der ID abfragen
                if actualQuery == 99:
                    clear_DB_Log()
                statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID WHERE M.ID = "+ str(attributeDateIn[0]) +" AND SNR.ID = " + str(SNRID[0])
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                InputTime = cursor.fetchone()

                # InputTime-String in Sekunden umwandeln
                InputSecond = convert_from_datestring(InputTime[0][0:-1])

                # Alle Rückmeldung ID's für Input ID abfragen
                if actualQuery == 99:
                    clear_DB_Log()
                statement = "SELECT R.ID FROM Rückmeldung R WHERE SNR_ID = " + str(SNRID[0])
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                RID_List = cursor.fetchall()
                
                # Rückmeldung ID's durchlaufen
                for RID in RID_List:

                    # Rückmeldung-Zeit der ID abfragen
                    if actualQuery == 99:
                        clear_DB_Log()
                    statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID WHERE M.ID = "+ str(attributeDateOut[0]) +" AND R.ID = " + str(RID[0])
                    cursor.execute(statement)
                    actualQuery = actualQuery + 1
                    OutputTime = cursor.fetchone()
                    
                    # OutputTime-String in Sekunden umwandeln
                    OutputSecond = convert_from_datestring(OutputTime[0][0:-1])

                    # Dauer in Liste aufnehmen
                    help_List.append(OutputSecond-InputSecond)
                    
                
                # Liste sortieren, dass die größte Dauer im 0-ten Element steht
                help_List.sort(reverse=True)
                
                # Dauern über 1h aussortieren
                if help_List[0] < 3600:
                    # Prüfen, ob Dauer min oder max darstellt
                    if help_List[0] < minTime:
                        minTime = help_List[0]
                    if help_List[0] > maxTime:
                        maxTime = help_List[0]
                    # Dauer zur AVG Berechnung hinzufügen
                    avgTime = avgTime + help_List[0]

                # Falls kein Einbezug der Dauer, Anzahl für AVG Berchnung mindern
                else:
                    avgDifference = avgDifference + 1 
            

            # Divisor zur AVG Berechnung pro FA
            divisor = len(SNRID_List)-avgDifference

            # Division durch 0 verhindern
            if divisor > 0:
                # AVG-Zeit pro FA in Sekunden
                avgTime = avgTime/divisor
                # AVG-Fail pro FA in Prozent
                avgFail = (avgFail/AnzahlProFA[0])*100
            
            # Ausgabe pro FA
            index = len(Result_List)
            Result_List.insert(index, [Teil[0], FA[0], AnzahlProFA[0], maxTime, minTime, avgTime, maxFail, minFail, avgFail])

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

    
