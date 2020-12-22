import mysql
import mysql.connector
import datetime, time

for lap in range(10):

    # Connection zu DB
    connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
    cursor = connection.cursor(buffered=True)

    # Ausgabeliste definieren
    List = list()

    # Log in DB clearen
    statement = "SET @@profiling = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 10000000;"
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
        Date = datetime.datetime.strptime(TimeString, "%Y-%m-%dT%H:%M:%S.%f")
        Second = time.mktime(Date.timetuple())
        return Second

    # Funktion zur Umwandlung Zeit-String in Sekunden
    def convert_from_s( seconds ): 
        minutes, seconds = divmod(seconds, 60) 
        hours, minutes = divmod(minutes, 60) 
        days, hours = divmod(hours, 24) 
        string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
        return string

    # Funktion zum Finden eines Strings in einer doppelt-verschachtelten Liste mit Rückgabe des Indexes
    def find(l, elem):
        for row, i in enumerate(l):
            try:
                i.index(elem)
            except ValueError:
                continue
            return row
        return -1

    # Maximumwert für minimale Zeit in Sekunden definieren
    second_min = convert_from_datestring("2100-12-31T23:59:59.000000")

    # ID des Merkmals DateIn
    statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'DateIn'"
    cursor.execute(statement)
    attributeDateIn = cursor.fetchone()

    # Alle Linien abfragen
    statement = "SELECT LINIE FROM LINIE ORDER BY LINIE"
    cursor.execute(statement)
    Linie_List = cursor.fetchall()

    # Alle Linien durchlaufen
    for Linie in Linie_List:

        # Alle FA einer Linie abfragen
        if actualQuery == 99:
            clear_DB_Log()
        statement = "SELECT SNR.FA FROM SNR WHERE SNR.LINIE = '"+Linie[0]+"' GROUP BY FA"
        cursor.execute(statement)
        actualQuery = actualQuery + 1
        FA_List = cursor.fetchall()

        # Liste für die FA Merkmale einer Linie deklarieren
        complete_list = list()

        i = 0

        # Alle FA durchlaufen
        for FA in FA_List:

            # Input-Zeiten und Teiltyp des FA für diese Linie abfragen, sortiert aufsteigend nach Zeit 
            if actualQuery == 99:
                clear_DB_Log()
            statement = "SELECT Ausprägung, SNR.TEIL FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE M.ID = "+ str(attributeDateIn[0]) +" AND SNR.FA = '"+FA[0]+"' AND SNR.LINIE = '"+ Linie[0] +"' AND SNR.SNR IS NOT NULL ORDER BY Ausprägung"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            Input_List = cursor.fetchall()

            # Anzahl der Input-Zeiten bestimmen
            length = len(Input_List)

            # Erste Input-Zeit, Teiltyp und letzte Input-Zeit für diesen FA der Liste hinzufügen
            complete_list.insert(i, [Input_List[0][0],Input_List[0][1],Input_List[length-1][0]])

            i = i + 1
        
        # Liste nach erster Input-Zeit sortieren
        complete_list.sort()

        # Ergebnisliste deklarieren
        Result_List = list()

        # Durch die Ergebnisliste einer Linie laufen 
        for j in range(0, (len(complete_list)-1)):
            
            if complete_list[j][2] == 'NULL':
                diff = -1
            else:
                # letzte InputZeit des aktuellen Elements in Sekunden umwandeln
                LastIn = complete_list[j][2]
                LastInSeconds = convert_from_datestring(LastIn[0:-1])

                # erste InputZeit des nächsten Elements in Sekunden umwandeln
                FirstInNext = complete_list[j+1][0]
                FirstInNextSecond = convert_from_datestring(FirstInNext[0:-1])

                # Zeitdifferenz berechnen
                diff = FirstInNextSecond - LastInSeconds

            if diff >= 0:
                # Wechsel von Teiltyp nach Teiltyp festhalten (Umrüstung)
                ChangeFromTo = complete_list[j][1] + complete_list[j+1][1]

                # Prüfen, ob Wechsel des Teiltyps bereits in Ergebnisliste vorhanden
                index = find(Result_List, ChangeFromTo)

                # Umrüstung noch nicht vorhanden
                if index == -1:
                    # aktuelle Länge der Ergebnisliste berechnen
                    position = len(Result_List)

                    # neues Element am Ende der Ergebnisliste einfügen [ChangeFromTo,min,max,avg,count]
                    Result_List.insert(position, [ChangeFromTo, diff, diff, diff, 1])
                
                # Umrüstung bereits vorhanden
                else:
                    # vorhandene Werte aus Liste auslesen
                    minTime = Result_List[index][1]
                    maxTime = Result_List[index][2]
                    avgTime = Result_List[index][3]
                    count = Result_List[index][4]

                    # Prüfen, ob min/max verändert werden müssen
                    if minTime > diff:
                        Result_List[index][1] = diff
                    if maxTime < diff:
                        Result_List[index][2] = diff
                    
                    # Dauer zur AVG Berechnung hinzufügen
                    avgTime = avgTime + diff
                    count = count + 1

                    # Dauer zurück in Liste schreiben
                    Result_List[index][3] = avgTime
                    Result_List[index][4] = count
        
        # Ergebnisliste nach ChangeFromTo ordnen (alphabetisch)
        Result_List.sort()
    
    List.append(Result_List)
    
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
