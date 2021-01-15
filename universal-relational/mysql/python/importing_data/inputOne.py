import mysql
import mysql.connector
import glob
import datetime

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
    pos_FA = 1
    pos_TEIL = 3
    pos_SNR = 4
    pos_LINIE = 5

    # Merkmale die ausgelesen werden sollen
    merkmalID_List = [1,'NULL',2,'NULL','NULL','NULL',3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

    # ID des ObjektTypen abfragen
    statement = "SELECT ID FROM ObjektTyp WHERE Bezeichnung = 'SNR'"
    cursor.execute(statement)
    result = cursor.fetchone()
    ObjektTypSNR = result[0]

    # Datensatz auslesen und vorbereiten
    datei = open(file,'r')
    val = datei.read()
    val = val[3:-2]
    data = val.split(';')
    
    k = 0
    flag_FA = 0
    flag_TEIL = 0
    flag_SNR = 0
    flag_LINIE = 0

    # einzelne Werte in SQL Syntax bringen
    for i in data:
        if i == "":
            data[k] = 'NULL'
            if k == pos_FA:
                flag_FA = 1
            if k == pos_TEIL:
                flag_TEIL = 1
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

    # Testen, ob Teil bereits vorhanden
    if flag_TEIL != 1:
        statement = "SELECT TEIL FROM TEIL WHERE TEIL = " + data[pos_TEIL]
        cursor.execute(statement)
        result = cursor.fetchone()
        if not result:
            statement = "INSERT INTO TEIL VALUES (" + data [pos_TEIL] + ")"
            cursor.execute(statement)
            connection.commit()

    # Testen, ob FA bereits vorhanden
    if flag_FA != 1:
        statement = "SELECT FA FROM FA WHERE FA = " + data[pos_FA]
        cursor.execute(statement)
        result = cursor.fetchone()
        if not result:
            statement = "INSERT INTO FA VALUES (" + data [pos_FA] + ")"
            cursor.execute(statement)
            connection.commit()

    # SNR Datensatz hinzufügen
    statement = "INSERT INTO SNR VALUES (NULL, " + data[pos_SNR] + "," + data [pos_FA] + "," + data [pos_TEIL] + "," + data [pos_LINIE] + ")"
    cursor.execute(statement)
    connection.commit()

    # ID der eben hinzugefügten SNR abfragen
    if flag_SNR != 1:
        statement = "SELECT MAX(ID) FROM SNR WHERE SNR.SNR = "+ data[pos_SNR]
        cursor.execute(statement)
        result = cursor.fetchone()
        SNRID = result[0]
    else:
        statement = "SELECT MAX(ID) FROM SNR"
        cursor.execute(statement)
        result = cursor.fetchone()
        SNRID = result[0]
    
    
    data[pos_SNR] = 'NULL'
    data[pos_LINIE] = 'NULL'
    data[pos_FA] = 'NULL'
    data[pos_TEIL] = 'NULL'

    # alle Merkmale der SNR durchlaufen
    for Merk_ID, value in zip(merkmalID_List, data):
        
        if value != 'NULL':
        
            # Testen, ob SNR Merkmal bereits besitzt
            statement = "SELECT ID FROM Objekt2Merkmal WHERE ObjektID = " + str(ObjektTypSNR) + " AND MerkmalID = " + str(Merk_ID) + " AND ObjektID = " + str(SNRID)
            cursor.execute(statement)
            result = cursor.fetchall()

            # Falls nein, Verbindung zwischen SNR und Merkmal herstellen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Objekt2Merkmal VALUES (NULL, " + str(Merk_ID) + "," + str(SNRID) + ", " + str(ObjektTypSNR) + ")"
                cursor.execute(statement)
                connection.commit()

            # Testen, ob Merkmalsausprägung für Merkmal bereits vohanden
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            cursor.execute(statement)
            result = cursor.fetchone()
            
            # Falls nein, Merkmalsausprägung des Merkmals einfügen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Merkmalsausprägung VALUES (NULL, " + str(Merk_ID) + "," + value + ")"
                cursor.execute(statement)
                connection.commit()

            # Abfragen der MerkmalsausprägungsID    
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            cursor.execute(statement)
            result = cursor.fetchone()
            AuspraegungsID = result[0]

            # Test, ob Merkmalsauspägung bereits mit Objekt verbunden 
            statement = "SELECT ID FROM Objekt2Merkmalsausprägung WHERE ObjektID = " + str(ObjektTypSNR) + " AND MerkmalsausprägungID = " + str(AuspraegungsID) + " AND ObjektID = " + str(SNRID)
            cursor.execute(statement)
            result = cursor.fetchall()  

            # Falls nein, Verbindung zwischen SNR und Merkmalsausprägung herstellen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Objekt2Merkmalsausprägung VALUES (NULL, " + str(AuspraegungsID) + ", " + str(SNRID) + ", " + str(ObjektTypSNR) + ")"
                cursor.execute(statement)
                connection.commit()

    # Prozesszeit auf DB abfragen
    statement = "SELECT SUM(DURATION) FROM INFORMATION_SCHEMA.PROFILING"
    cursor.execute(statement)
    DurationDB = cursor.fetchone()

    cursor.close()
    connection.close()

    return DurationDB[0]