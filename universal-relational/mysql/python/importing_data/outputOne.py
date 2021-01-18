import mysql
import mysql.connector
import glob
import datetime, time

# Funktion zur Umwandlung Zeit-String in Sekunden
def convert_from_datestring( TimeString ): 
    Date = datetime.datetime.strptime(TimeString, "%Y-%m-%dT%H:%M:%S.%f")
    Second = time.mktime(Date.timetuple())
    return Second

def insert (file):
    # Connection zu DB
    connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_4")
    cursor = connection.cursor()

    # Log in DB clearen
    statement = "SET @@profiling = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 0"
    cursor.execute(statement)
    statement = "SET @@profiling_history_size = 100;"
    cursor.execute(statement)
    statement = "SET @@profiling = 1"
    cursor.execute(statement)

    # Positionen der Merkmale im Input
    pos_SNR = 0
    pos_LINIE = 1
    pos_DATE = 17

    # Merkmale die ausgelesen werden sollen
    merkmID_list = ['NULL','NULL',24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]

    # ID der ObjektTypen abfragen
    statement = "SELECT ID FROM ObjektTyp WHERE Bezeichnung = 'Rückmeldung'"
    cursor.execute(statement)
    result = cursor.fetchone()
    ObjektTypRückmeldung = result[0]

    # ID des Merkmals DateIn
    statement = "SELECT ID FROM Merkmal WHERE Bezeichnung = 'DateIn'"
    cursor.execute(statement)
    attributeDateIn = cursor.fetchone()

    # Datensatz auslesen und vorbereiten
    datei = open(file,'r')
    val = datei.read()
    val = val[3:-2]
    data = val.split(';')

    k = 0
    flag_SNR = 0
    flag_LINIE = 0

    # Werte in SQL Syntax bringen und überprüfen, welche Merkmale vorhanden sind
    for i in data:
        
        if i == "":
            data[k] = 'NULL'
            if k == pos_SNR:
                flag_SNR = 1
            if k == pos_LINIE:
                flag_LINIE = 1
        else:
            data[k] = "'" + data[k] + "'"
        k = k + 1
    
    # Testen, ob Linie bereits vorhanden
    if flag_LINIE != 1:
        statement = "SELECT LINIE FROM LINIE WHERE LINIE = " + data[pos_LINIE]
        cursor.execute(statement)
        result = cursor.fetchone()
        if not result:
            statement = "INSERT INTO LINIE VALUES (" + data [pos_LINIE] + ")"
            cursor.execute(statement)
            connection.commit()

    # Testen, ob SNR leer
    if flag_SNR == 1:
        statement = "INSERT INTO Rückmeldung VALUES (NULL, NULL, " + data [pos_LINIE] + ", NULL )"
        cursor.execute(statement)
        connection.commit()
    else:
        # SNR_ID herausfinden
        statement = "SELECT SNR.ID, MA.Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung AS O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung AS MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.SNR = "+ data[pos_SNR] +" AND M.ID = "+ str(attributeDateIn[0])
        cursor.execute(statement)
        result = cursor.fetchall()

        # keinen Input gefunden
        if cursor.rowcount == 0:
            statement = "INSERT INTO Rückmeldung VALUES (NULL, " + data[pos_SNR] + "," + data[pos_LINIE] + ", NULL)"
            cursor.execute(statement)
            connection.commit()

        elif cursor.rowcount == 1:
            # keine SNR in Tabelle SNR
            if not result:
                statement = "INSERT INTO Rückmeldung VALUES (NULL, " + data[pos_SNR] + "," + data[pos_LINIE] + ", NULL)"
                cursor.execute(statement)
                connection.commit()

            # genau eine SNR in Tabelle SNR
            else:
                diff = 0

                # Umrechnung der Output-Zeit in Sekunden für Zuordnung 
                second_out = convert_from_datestring(data[pos_DATE][1:-1])

                # Umrechnung der Input-Zeit in Sekunden für Zuordnung 
                second_in = convert_from_datestring(result[0][1][0:-1])

                # Zeitdifferenz berechnen
                diff = second_out - second_in

                # Testen, ob Differenz negativ
                if diff > 0:
                    SNR_ID = result[0][0]
                    statement = "INSERT INTO Rückmeldung VALUES (NULL, " + data[pos_SNR] + "," + data[pos_LINIE] + ", " + str(SNR_ID) + ")"
                    cursor.execute(statement)
                    connection.commit()
                else:
                    statement = "INSERT INTO Rückmeldung VALUES (NULL, " + data[pos_SNR] + "," + data[pos_LINIE] + ", NULL)"
                    cursor.execute(statement)
                    connection.commit()

        
        # mehrere SNR in Tabelle SNR
        elif cursor.rowcount > 1:
            diff = 0
            count = 0

            # Umrechnung der Output-Zeit in Sekunden für Zuordnung
            second_out = convert_from_datestring(data[pos_DATE][1:-1])

            # Ergebnismenge durchlaufen
            for res in result:

                # Umrechnung der Input-Zeit in Sekunden für Zuordnung 
                second_in = convert_from_datestring(res[1][0:-1])

                # Zeitdifferenz berechnen
                diff = second_out - second_in

                # erste Differenz auf min_diff setzen
                if (count == 0) & (diff < 0):
                    SNR_ID = "NULL"
                    continue

                if (count == 0) & (diff > 0):
                    min_diff = diff
                    count = 1

                # Testen, ob diff kleiner  
                if diff <= min_diff:
                    # Testen, ob diff negativ
                    if diff > 0:
                        min_diff = diff
                        SNR_ID = res[0]
                
            statement = "INSERT INTO Rückmeldung VALUES (NULL, " + data[pos_SNR] + "," + data[pos_LINIE] + ", " + str(SNR_ID) + ")" 
            cursor.execute(statement)
            connection.commit()           
                
    # ID der eben hinzugefügten Output SNR abfragen
    statement = "SELECT MAX(ID) FROM Rückmeldung"
    cursor.execute(statement)
    result = cursor.fetchone()
    RückmeldungID = result[0]
    
    # alle Merkmale der Output SNR durchlaufen
    data[pos_SNR] = 'NULL'
    data[pos_LINIE] = 'NULL'

    for Merk_ID, value in zip(merkmID_list, data):
        
        if value != 'NULL':
            # Testen, ob SNR Merkmal bereits besitzt
            statement = "SELECT ID FROM Objekt2Merkmal WHERE ObjektTyp = " + str(ObjektTypRückmeldung) + " AND MerkmalID = " + str(Merk_ID) + " AND ObjektID = " + str(RückmeldungID)
            cursor.execute(statement)
            result = cursor.fetchall() 

            # Falls nein, Verbindung zwischen SNR und Merkmal herstellen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Objekt2Merkmal VALUES (NULL, " + str(Merk_ID) + "," + str(RückmeldungID) + ", " + str(ObjektTypRückmeldung) + ")"
                cursor.execute(statement)
                connection.commit()

            # Testen, ob Merkmalsausprägung für Merkmal bereits vohanden
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            cursor.execute(statement)
            result = cursor.fetchall()
            
            # Falls nein, Merkmalsausprägung einfügen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Merkmalsausprägung VALUES (NULL, " + str(Merk_ID) + "," + value + ")"
                cursor.execute(statement)
                connection.commit()

            # Abfragen der MerkmalsauspräungsID    
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            cursor.execute(statement)
            result = cursor.fetchone()
            AusP_ID = result[0]

            # Test, ob Merkmalsauspägung bereits mit Objekt verbunden
            statement = "SELECT ID FROM Objekt2Merkmalsausprägung WHERE ObjektTyp = " + str(ObjektTypRückmeldung) + " AND MerkmalsausprägungID = " + str(AusP_ID) + " AND ObjektID = " + str(RückmeldungID)
            cursor.execute(statement)
            result = cursor.fetchall()  

            # Falls nein, Verbindung zwischen SNR und Merkmalsausprägung herstellen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Objekt2Merkmalsausprägung VALUES (NULL, " + str(AusP_ID) + ", " + str(RückmeldungID) + ", " + str(ObjektTypRückmeldung) + ")"
                cursor.execute(statement)
                connection.commit()

    # Prozesszeit auf DB abfragen
    statement = "SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING"
    cursor.execute(statement)
    DurationDB = cursor.fetchone()

    cursor.close()
    connection.close()

    return DurationDB[0]