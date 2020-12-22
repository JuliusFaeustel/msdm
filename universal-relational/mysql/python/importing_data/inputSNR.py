import mysql
import mysql.connector
import glob
import datetime

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_3")
cursor = connection.cursor()

# alle Files aus Ordner
files = glob.glob("C:/Users/picht/Desktop/Projektseminar I-490/htw/in/00493533.txt")


# Summe der Ladezeit
#time_sum = 0

# Positionen der Merkmale im Input
pos_FA = 1
pos_TEIL = 3
pos_SNR = 4
pos_LINIE = 5

merkmID_list = [1,'NULL',2,'NULL','NULL','NULL',3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

j = 0


# ID des ObjektTypen abfragen
statement = "SELECT ID FROM ObjektTyp WHERE Bezeichnung = 'SNR'"
cursor.execute(statement)
result = cursor.fetchone()
Objekt_ID = result[0]

now1 = datetime.datetime.now()
# Durchlaufen jedes Dokuments
for filename in files:
    
    # Datensatz auslesen und vorbereiten
    datei = open(filename,'r')
    val = datei.read()
    val = val[3:-2]
    dat = val.split(';')
    
    k = 0
    flag_FA = 0
    flag_TEIL = 0
    flag_SNR = 0
    flag_LINIE = 0
    # Werte in SQL Syntax bringen
    for i in dat:
        if i == "":
            dat[k] = 'NULL'
            if k == 1:
                flag_FA = 1
            if k == 3:
                flag_TEIL = 1
            if k == 4:
                flag_SNR = 1
            if k == 5:
                flag_LINIE = 1
        else:
            dat[k] = "'" + dat[k] + "'"
            
        k = k + 1

    # Testen, ob Linie bereits vorhanden
    if flag_LINIE != 1:
        statement = "SELECT LINIE FROM LINIE WHERE LINIE = " + dat[pos_LINIE]
        cursor.execute(statement)
        result = cursor.fetchone()
        if not result:
            statement = "INSERT INTO LINIE VALUES (" + dat [pos_LINIE] + ")"
            cursor.execute(statement)
            connection.commit()

    # Testen, ob Teil bereits vorhanden
    if flag_TEIL != 1:
        statement = "SELECT TEIL FROM TEIL WHERE TEIL = " + dat[pos_TEIL]
        cursor.execute(statement)
        result = cursor.fetchone()
        if not result:
            statement = "INSERT INTO TEIL VALUES (" + dat [pos_TEIL] + ")"
            cursor.execute(statement)
            connection.commit()

    # Testen, ob FA bereits vorhanden
    if flag_FA != 1:
        statement = "SELECT FA FROM FA WHERE FA = " + dat[pos_FA]
        cursor.execute(statement)
        result = cursor.fetchone()
        if not result:
            statement = "INSERT INTO FA VALUES (" + dat [pos_FA] + ")"
            cursor.execute(statement)
            connection.commit()

    # SNR Datensatz hinzufügen
    statement = "INSERT INTO SNR VALUES (NULL, " + dat[pos_SNR] + "," + dat [pos_FA] + "," + dat [pos_TEIL] + "," + dat [pos_LINIE] + ")"
    cursor.execute(statement)
    connection.commit()

    # ID der eben hinzugefügten SNR abfragen
    if flag_SNR != 1:
        statement = "SELECT MAX(ID) FROM SNR WHERE SNR.SNR = "+ dat[pos_SNR]
        cursor.execute(statement)
        result = cursor.fetchone()
        SNR_ID = result[0]
    else:
        statement = "SELECT MAX(ID) FROM SNR"
        cursor.execute(statement)
        result = cursor.fetchone()
        SNR_ID = result[0]
    
    # alle Merkmale der SNR durchlaufen
    dat[pos_SNR] = 'NULL'
    dat[pos_LINIE] = 'NULL'
    dat[pos_FA] = 'NULL'
    dat[pos_TEIL] = 'NULL'
    for Merk_ID, value in zip(merkmID_list, dat):
        if value != 'NULL':
           
            # # Testen, ob SNR Merkmal bereits besitzt
            # statement = "SELECT ID FROM Objekt2Merkmal WHERE ObjektID = " + str(Objekt_ID) + " AND MerkmalID = " + str(Merk_ID) + " AND ObjektID = " + str(SNR_ID)
            # cursor.execute(statement)
            # result = cursor.fetchall()

            # Falls nein, Verbindung zwischen SNR und Merkmal herstellen
            #if cursor.rowcount == 0:
            statement = "INSERT INTO Objekt2Merkmal VALUES (NULL, " + str(Merk_ID) + "," + str(SNR_ID) + ", " + str(Objekt_ID) + ")"
            cursor.execute(statement)
            connection.commit()

            # Testen, ob Merkmalsausprägung für Merkmal bereits vohanden
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            #print(statement)
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
            AusP_ID = result[0]

            # # Test, ob Merkmalsauspägung bereits mit Objekt verbunden 
            # statement = "SELECT ID FROM Objekt2Merkmalsausprägung WHERE ObjektID = " + str(Objekt_ID) + " AND MerkmalsausprägungID = " + str(AusP_ID) + " AND ObjektID = " + str(SNR_ID)
            # cursor.execute(statement)
            # result = cursor.fetchall()  

            # Falls nein, Verbindung zwischen SNR und Merkmalsausprägung herstellen
            #if cursor.rowcount == 0:
            statement = "INSERT INTO Objekt2Merkmalsausprägung VALUES (NULL, " + str(AusP_ID) + ", " + str(SNR_ID) + ", " + str(Objekt_ID) + ")"
            cursor.execute(statement)
            connection.commit()

 
    j = j + 1
    print(j)
    
    # time_sum = time_sum + erg
    # if j%100 == 0:
    #     print("SUM: " + str(time_sum/1000) + "s")
    #     print("AVG: " + str(time_sum/100) + "ms")
    #     time_sum = 0
    
now2 = datetime.datetime.now()
erg = now2-now1
erg = int(erg.total_seconds()/60)
print(str(erg) + " min")
print('All Data INPUT loaded')
cursor.close()
connection.close()