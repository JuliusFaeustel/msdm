import pyodbc
import datetime, time
from time import process_time_ns

start = process_time_ns()

# Verbindung zu DB aufbauen
server = 'DESKTOP-0IJEV10\\SQLEXPRESS'
database = 'project'
username = 'paul'
password = '123'

connection = pyodbc.connect(driver = '{ODBC Driver 17 for SQL Server}',server = server , database = database, UID = username, PWD = password)
cursor = connection.cursor()

# Ausgabeliste definieren
Result_List = list()

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
Teil_List = cursor.fetchall()

# Alle Teiltypen durchlaufen
for Teil in Teil_List:
        
    # Anzahl gefertigter Teile pro Teiltyp ermitteln
    statement = "SELECT COUNT(*) FROM (SELECT SNR.SNR FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE TEIL = 'A' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
    cursor.execute(statement)
    AnzahlProTyp = cursor.fetchone()

    # Alle SNR mit diesem Teiltyp abfragen, die mehr als einen Input haben
    statement = "SELECT SNR.SNR FROM SNR WHERE SNR.TEIL = '" + Teil[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(DISTINCT(ID)) > 1"
    cursor.execute(statement)
    Ausschuss_List = cursor.fetchall()

    # Varibalendeklaration
    minTime = second_min
    maxTime = 0
    avgTime = 0
    avgFail = 0
    countTime = 0

    # Alle SNR, die Ausschuss haben, durchlaufen
    for Ausschuss in Ausschuss_List:

        # ID und Zeit-Ausprägung der Inputs abfragen, geordnet nach Datum aufsteigend für SNR
        statement = "SELECT SNR.ID, MA.Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung AS O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung AS MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.SNR = '" + Ausschuss[0] + "' AND M.ID = "+ str(attributeDateIn[0]) +" ORDER BY Ausprägung"
        cursor.execute(statement)
        Input_List = cursor.fetchall()

        # Ausschuss ist alles mehr als ein Input 
        AnzahlFail = len(Input_List)-1

        # Ausschuss zur AVG Berechnung hinzufügen
        avgFail = avgFail + AnzahlFail
        
        nextElement = 1
        diffTime = 0

        for Input in Input_List:

            # Zeit-Ausprägungen der Rückmeldungen der Input ID abfragen, geordent nach Datum absteigend
            statement = "SELECT MA.Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung AS O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung AS MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE R.SNR_ID = " + str(Input[0]) + " AND M.ID = "+ str(attributeDateOut[0]) +" ORDER BY Ausprägung DESC"
            cursor.execute(statement)
            OutputTime = cursor.fetchone()
            
            # Wenn kein Datum vorhanden
            if not OutputTime:
                nextElement = nextElement + 1
                continue

            # Wenn Datum vorhanden, OutputTime-String des aktuellen Inputs in Sekunden umwandeln
            OutputSecond = convert_from_datestring(OutputTime[0][0:-1])
            
            # Prüfen, ob nach aktuellem Input ein nächster Input folgt 
            if nextElement < len(Input_List):
                
                # InputTime-String des nächsten Inputs in Sekunden umwandeln
                NextInputSecond = convert_from_datestring(Input_List[nextElement][1][0:-1])
                
                # Differenz berechnen
                diffTime = NextInputSecond - OutputSecond
                
                # Prüfen, ob Dauer min oder max darstellt
                if diffTime < minTime:
                    minTime = diffTime
                if diffTime > maxTime:
                    maxTime = diffTime

                # Dauer zur AVG Berechnung hinzufügen
                avgTime = avgTime + diffTime
                countTime = countTime + 1
            
            nextElement = nextElement +1
            
    # Prüfen, ob minTime noch initial ist und ggfls. auf 0 setzen     
    if minTime == second_min:
        minTime = 0
    
    # Division durch 0 verhindern
    if countTime > 0:
        avgTime = avgTime / countTime
        avgFail = (avgFail/AnzahlProTyp[0])

    # Ausgabe
    index = len(Result_List)
    Result_List.insert(index, [Teil[0], maxTime, minTime, avgTime, avgFail])

connection.close()

stop = process_time_ns()
DurationScript = (stop-start)/10**9
print("Durchlaufzeit Skript: "+str(DurationScript)+" s")
     




