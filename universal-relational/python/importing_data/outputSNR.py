import mysql
import mysql.connector
import glob
import datetime, time

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor()

# alle Files aus Ordner
files = glob.glob("C:/Users/picht/Desktop/Projektseminar I-490/htw/out/*.txt")

# Summe der Ladezeit
#time_sum = 0

# Positionen der Merkmale im Input
pos_SNR = 0
pos_LINIE = 1
pos_DATE = 17

merkmID_list = ['NULL','NULL',24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]

j = 0

# ID des ObjektTypen abfragen
statement = "SELECT ID FROM ObjektTyp WHERE Bezeichnung = 'Rückmeldung'"
cursor.execute(statement)
result = cursor.fetchone()
Objekt_ID_Rück = result[0]

statement = "SELECT ID FROM ObjektTyp WHERE Bezeichnung = 'SNR'"
cursor.execute(statement)
result = cursor.fetchone()
Objekt_Typ_SNR = result[0]
now1 = datetime.datetime.now()
# Durchlaufen jedes Dokuments
for filename in files:
    
    
    # Datensatz auslesen und vorbereiten
    datei = open(filename,'r')
    val = datei.read()
    val = val[3:-2]
    dat = val.split(';')


    
    k = 0
    flag_SNR = 0
    flag_LINIE = 0
    # Werte in SQL Syntax bringen und überprüfen, welche Merkmale vorhanden sind
    for i in dat:
        
        if i == "":
            dat[k] = 'NULL'
            if k == 0:
                flag_SNR = 1
            if k == 1:
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

    # Testen, ob SNR leer
    if dat[pos_SNR] == 'NULL':
        statement = "INSERT INTO Rückmeldung VALUES (NULL, NULL, " + dat [pos_LINIE] + ", NULL )"
        #print("NO COUNT "+statement)
        cursor.execute(statement)
        connection.commit()
    else:
        # SNR_ID herausfinden
        statement = "SELECT SNR.ID, MA.Ausprägung from SNR join Objekt2Merkmalsausprägung as O2MA on SNR.ID = O2MA.ObjektID join Merkmalsausprägung as MA on O2MA.MerkmalsausprägungID = MA.ID WHERE O2MA.ObjektTyp = "+ str(Objekt_Typ_SNR) +" AND SNR = " + dat[pos_SNR] + " AND MerkmalID = 1"
        cursor.execute(statement)
        result = cursor.fetchall()
        #print("ROWCOUNT: " + str(cursor.rowcount))
        #print(result[0][1])

        if cursor.rowcount == 0:
            statement = "INSERT INTO Rückmeldung VALUES (NULL, " + dat[pos_SNR] + "," + dat[pos_LINIE] + ", NULL)"
            #print("COUNT: 0 "+statement)
            cursor.execute(statement)
            connection.commit()

        elif cursor.rowcount == 1:
            # keine SNR in Tabelle SNR
            if not result:
                statement = "INSERT INTO Rückmeldung VALUES (NULL, " + dat[pos_SNR] + "," + dat[pos_LINIE] + ", NULL)"
                #print("COUNT: 1 "+statement)
                cursor.execute(statement)
                connection.commit()
            # genau eine SNR in Tabelle SNR
            else:
                diff = 0
                count = 0
                # Umrechnung der Zeit für Zuordnung nötig
                date_out = datetime.datetime.strptime(dat[pos_DATE][1:-1], "%Y-%m-%dT%H:%M:%S.%f")
                second_out = time.mktime(date_out.timetuple())
                # Ergebnismenge durchlaufen
                date_in = datetime.datetime.strptime(result[0][1][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
                second_in = time.mktime(date_in.timetuple())
                diff = second_out - second_in
                # Testen, ob diff negativ
                if diff > 0:
                    SNR_ID = result[0][0]
                    statement = "INSERT INTO Rückmeldung VALUES (NULL, " + dat[pos_SNR] + "," + dat[pos_LINIE] + ", " + str(SNR_ID) + ")" 
                    #print(statement)
                    cursor.execute(statement)
                    connection.commit()
                else:
                    statement = "INSERT INTO Rückmeldung VALUES (NULL, " + dat[pos_SNR] + "," + dat[pos_LINIE] + ", NULL)" 
                    #print(statement)
                    cursor.execute(statement)
                    connection.commit()

           
        # mehrere SNR in Tabelle SNR
        if cursor.rowcount > 1:
            diff = 0
            count = 0
            # Umrechnung der Zeit für Zuordnung nötig
            date_out = datetime.datetime.strptime(dat[pos_DATE][1:-1], "%Y-%m-%dT%H:%M:%S.%f")
            second_out = time.mktime(date_out.timetuple())
            # Ergebnismenge durchlaufen
            for res in result:
                date_in = datetime.datetime.strptime(res[1][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
                second_in = time.mktime(date_in.timetuple())
                diff = second_out - second_in
                # erste Differenz auf min_diff setzen
                if (count == 0) & (diff > 0):
                    min_diff = diff
                    count = 1
                # Testen, ob diff kleiner  
                if diff <= min_diff:
                    # Testen, ob diff negativ
                    if diff > 0:
                        min_diff = diff
                        SNR_ID = res[0]
                
            statement = "INSERT INTO Rückmeldung VALUES (NULL, " + dat[pos_SNR] + "," + dat[pos_LINIE] + ", " + str(SNR_ID) + ")" 
            #print(statement)
            cursor.execute(statement)
            connection.commit()           
                  
    # ID der eben hinzugefügten Output SNR abfragen
    statement = "SELECT MAX(ID) FROM Rückmeldung"
    cursor.execute(statement)
    result = cursor.fetchone()
    SNR_ID = result[0]
    #print(statement)
    #print(SNR_ID)
    
    # alle Merkmale der Output SNR durchlaufen
    dat[pos_SNR] = 'NULL'
    dat[pos_LINIE] = 'NULL'
    #print(dat)
    for Merk_ID, value in zip(merkmID_list, dat):
        if value != 'NULL':
            # # Testen, ob SNR Merkmal bereits besitzt
            # statement = "SELECT ID FROM Objekt2Merkmal WHERE ObjektTyp = " + str(Objekt_ID) + " AND MerkmalID = " + str(Merk_ID) + " AND ObjektID = " + str(SNR_ID)
            # cursor.execute(statement)
            # result = cursor.fetchall() 

            # Falls nein, Verbindung zwischen SNR und Merkmal herstellen
            # if cursor.rowcount == 0:
            statement = "INSERT INTO Objekt2Merkmal VALUES (NULL, " + str(Merk_ID) + "," + str(SNR_ID) + ", " + str(Objekt_ID_Rück) + ")"
            cursor.execute(statement)
            connection.commit()

            # Testen, ob Merkmalsausprägung für Merkmal bereits vohanden
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            #print(statement)
            cursor.execute(statement)
            result = cursor.fetchall()
            
            # Falls nein, Merkmalsausprägung des Merkmals einfügen
            if cursor.rowcount == 0:
                statement = "INSERT INTO Merkmalsausprägung VALUES (NULL, " + str(Merk_ID) + "," + value + ")"
                #print(statement)
                cursor.execute(statement)
                connection.commit()

            # Abfragen der MerkmalsauspräungsID    
            statement = "SELECT ID FROM Merkmalsausprägung WHERE MerkmalID = " + str(Merk_ID) + " AND Ausprägung = " + value
            cursor.execute(statement)
            result = cursor.fetchone()
            AusP_ID = result[0]

            # # Test, ob Merkmalsauspägung bereits mit Objekt verbunden
            # statement = "SELECT ID FROM Objekt2Merkmalsausprägung WHERE ObjektTyp = " + str(Objekt_ID) + " AND MerkmalsausprägungID = " + str(AusP_ID) + " AND ObjektID = " + str(SNR_ID)
            # cursor.execute(statement)
            # result = cursor.fetchall()  

            # Falls nein, Verbindung zwischen SNR und Merkmalsausprägung herstellen
            #if cursor.rowcount == 0:
            statement = "INSERT INTO Objekt2Merkmalsausprägung VALUES (NULL, " + str(AusP_ID) + ", " + str(SNR_ID) + ", " + str(Objekt_ID_Rück) + ")"
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
print('All Data OUTPUT loaded')
cursor.close()
connection.close()