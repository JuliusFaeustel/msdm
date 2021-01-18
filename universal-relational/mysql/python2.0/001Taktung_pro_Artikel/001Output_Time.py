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

    second_min = convert_from_datestring("2100-12-31T23:59:59.000000")

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

            if actualQuery == 99:
                clear_DB_Log() 
            statement = "SELECT SNR.ID, MA.Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID WHERE M.ID = 1 AND SNR.FA ='" + FA[0] +"'"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            Input_List = cursor.fetchall()
            
            str1 = ''
            for ele in Input_List:  
                str1 = str1 + str(ele[0]) + ','
            str1 = str1[:-1]

            if actualQuery == 99:
                clear_DB_Log() 
            statement = "SELECT R.SNR_ID, MAX(MA.Ausprägung) FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON ((R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2)) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON ((O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2)) JOIN Merkmal M ON O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID WHERE M.ID = 39 AND R.SNR_ID IN ("+ str1 +") GROUP BY R.SNR_ID"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            Output_List = cursor.fetchall()

            minTime = second_min
            maxTime = 0
            avgTime = 0
            divisor = 0
            minFail = 0
            maxFail = 0
            avgFail = 0

            for Input in Input_List:

                for i in range(len(Output_List)):
                    if Output_List[i][0] == Input[0]:
                        InputTime = convert_from_datestring(Input[1][0:-1])
                        OutputTime = convert_from_datestring(Output_List[i][1][0:-1])
                        diff = OutputTime - InputTime
                        if diff < 3600:
                            if diff < minTime:
                                minTime = diff
                            if diff > maxTime:
                                maxTime = diff
                            avgTime = avgTime + diff
                            divisor = divisor + 1
                    else:
                        continue
            
            # AVG-Zeit pro FA in Sekunden
            avgTime = avgTime/divisor
            
            # Alle SNR abfragen, die mehr als einen Input in diesem FA haben
            if actualQuery == 99:
                clear_DB_Log() 
            statement = "SELECT SNR.SNR FROM SNR WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(ID) > 1"
            cursor.execute(statement)
            actualQuery = actualQuery + 1
            AusschussSNR_List = cursor.fetchall()

            str2 = ''
            for ele2 in AusschussSNR_List:  
                str2 = str2 + str(ele2[0]) + ','
            str2 = str2[:-1]

            if str2 != '':
                if actualQuery == 99:
                    clear_DB_Log() 
                statement = "SELECT COUNT(ID), SNR FROM SNR WHERE FA = '" + FA[0] + "' AND SNR IN ("+ str2 +") GROUP BY SNR.SNR"
                cursor.execute(statement)
                actualQuery = actualQuery + 1
                Ausschuss_List = cursor.fetchall()

                maxFail = max(Ausschuss_List)[0]-1
                minFail = min(Ausschuss_List)[0]-1
                sumFail = 0
                for i in range(len(Ausschuss_List)):
                    sumFail = sumFail + Ausschuss_List[i][0] - 1

                avgFail = (sumFail/AnzahlProFA[0])*100


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
                    





        

