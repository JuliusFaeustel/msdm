import mysql
import mysql.connector
import datetime, time

# Verbindung zu DB aufbauen
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor(buffered=True)

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

# Alle Teiltypen abfragen
statement = "SELECT TEIL FROM TEIL ORDER BY TEIL"
cursor.execute(statement)
Teil_List = cursor.fetchall()

i = 0
for Teil in Teil_List:
    
    # Alle LadungsträgerIn für den Teiltyp abfragen
    statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.TEIL = '"+Teil[0]+"' AND MA.MerkmalID = 21 GROUP BY Ausprägung ORDER BY Ausprägung"
    cursor.execute(statement)
    LagerIn_List = cursor.fetchall()
    
    # Alle LadungsträgerIn für den Teiltyp durchlaufen
    for LagerIn in LagerIn_List:

        # Anzahl gefertigter Teile pro Ladungsträger des Teiltyps ermitteln
        statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR 	JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.TEIL = '"+Teil[0]+"' AND MA.MerkmalID = 21 AND MA.Ausprägung = '"+LagerIn[0]+"' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
        cursor.execute(statement)
        AnzahlProLad = cursor.fetchone()

        # SNR ID's des Teiltypen abrufen, die auf dem aktuellen Ladungsträger gefertigt wurden
        statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.TEIL = '"+Teil[0]+"' AND MA.MerkmalID = 21 AND MA.Ausprägung = '"+LagerIn[0]+"' AND SNR.SNR IS NOT NULL"
        cursor.execute(statement)
        Input_List = cursor.fetchall()

        #Variablendeklaration
        minTime = second_min
        maxTime = 0
        avgTime = 0
        counter = 0

        # Alle SNR ID's für Ladungsträger durchlaufen
        for InputID in Input_List:

            # Input-Date für die SNR ID abfragen
            statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.MerkmalID = 1 AND SNR.ID = "+str(InputID[0])
            cursor.execute(statement)
            InputDate = cursor.fetchone()

            # InputTime-String in Sekunden umwandeln
            InputDateSecond = convert_from_datestring(InputDate[0][0:-1])

            # Rückmeldungen zur Input ID abfragen
            statement = "SELECT R.ID FROM Rückmeldung R WHERE SNR_ID = "+str(InputID[0])
            cursor.execute(statement)
            Output_List = cursor.fetchall()

            # Liste der Differenzen deklarieren
            diff_List = list()

            # Alle Rückmeldung ID's durchlaufen
            for OutputID in Output_List:

                # Output-Date für die Rückmeldung ID abfragen
                statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID WHERE MA.MerkmalID = 39 AND R.ID = " + str(OutputID[0])
                cursor.execute(statement)
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

connection.close()
