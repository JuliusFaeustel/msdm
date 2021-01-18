import matplotlib as mlp
import matplotlib.pyplot as plt

import mysql
import mysql.connector
import datetime, time


# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mysql_new/Ergebnisse/004Ladungsträger/Ladungsträger.txt","w")
dateiCSV = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mysql_new/Ergebnisse/004Ladungsträger/Ladungsträger.csv","w")

dateiCSV.write("LAGER;DURATION;START;END;COUNT\n")

# Flag zur Boxplotzeichnung pro Teiltyp
BoxFlag = False

# Verbindung zu DB aufbauen
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor(buffered=True)

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

if BoxFlag == True:
    BoxTime_List = list()

# Alle Ladungsträger durchlaufen
for LagerIn in LagerIn_List:

    # Anzahl gefertigter Teile pro Ladungsträger ermitteln
    statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND SNR.SNR IS NOT NULL GROUP BY SNR) Q"
    cursor.execute(statement)
    AnzahlProLad = cursor.fetchone()

    # SNR ID's abrufen, die auf dem aktuellen Ladungsträger gefertigt wurden
    statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND M.ID = "+ str(attributeLagerIn[0]) +" AND SNR.SNR IS NOT NULL"
    cursor.execute(statement)
    Input_List = cursor.fetchall()

    str1 = ''
    for ele in Input_List:  
        str1 = str1 + str(ele[0]) + ','
    str1 = str1[:-1]

    statement = "SELECT MIN(Ausprägung) FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE SNR.ID IN ("+ str1 +") AND M.ID = "+ str(attributeDateIn[0])
    cursor.execute(statement)
    InputDate = cursor.fetchone()
    InputDateSeconds = convert_from_datestring(InputDate[0][0:-1])
    minInputDate = InputDate[0]
    
    statement = "SELECT MAX(Ausprägung) FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = R.ID AND o2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2) JOIN Merkmal M ON (O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID) WHERE R.SNR_ID IN ("+ str1 +") AND M.ID = "+ str(attributeDateOut[0])
    cursor.execute(statement)
    OutputDate = cursor.fetchone()
    OutputDateSeconds = convert_from_datestring(OutputDate[0][0:-1])
    maxOutputDate = OutputDate[0]
    
    Dauer = OutputDateSeconds - InputDateSeconds

    if BoxFlag == True:
        BoxTime_List.append(Dauer/3600)

    # Ausgabe
    datei.write("Ladungsträger: "+LagerIn[0]+"        Anzahl: "+str(AnzahlProLad[0])+"        Dauer: "+convert_from_s(Dauer)+"        Start: "+minInputDate[:19]+"         Ende: "+maxOutputDate[:19]+"\n")
    dateiCSV.write(LagerIn[0] +";"+ str(format(Dauer, '.2f')) +";"+ minInputDate[:19] +";"+ maxOutputDate[:19] +";"+ str(AnzahlProLad[0]) +"\n")

# Boxplot zeichnen
if BoxFlag == True:
    plt.figure(1)
    plt.title('Ladungsträger gesamt')
    plt.ylabel('Stunden')
    plt.axis
    plt.boxplot(BoxTime_List, labels=['Alle Ladungsträger'], showfliers=False)
    plt.savefig('C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/004Ladungsträger/Ladungsträger.png')
    plt.close(1)

datei.close()
dateiCSV.close()
connection.close()

        


    