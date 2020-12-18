import matplotlib as mlp
import matplotlib.pyplot as plt

import mysql
import mysql.connector
import datetime, time

# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/004Ladungsträger/Ladungsträger.txt","w")

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

# Alle LadungsträgerIn abfragen
statement = "SELECT Ausprägung FROM Merkmalsausprägung WHERE MerkmalID = 21 ORDER BY Ausprägung"
cursor.execute(statement)
LagerIn_List = cursor.fetchall()

# Variablendeklaration
Dauer = 0

if BoxFlag == True:
    BoxTime_List = list()

# Alle Ladungsträger durchlaufen
for LagerIn in LagerIn_List:

    # Anzahl gefertigter Teile pro Ladungsträger ermitteln
    statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND MA.MerkmalID = 21 AND SNR.SNR IS NOT NULL GROUP BY SNR) Q"
    cursor.execute(statement)
    AnzahlProLad = cursor.fetchone()

    # SNR ID's abrufen, die auf dem aktuellen Ladungsträger gefertigt wurden
    statement = "SELECT SNR.ID FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE MA.Ausprägung = '"+LagerIn[0]+"' AND MA.MerkmalID = 21 AND SNR.SNR IS NOT NULL"
    cursor.execute(statement)
    Input_List = cursor.fetchall()

    # Variablendeklaration
    minInputSecond = second_min
    minInputDate = ''
    maxOutputSecond = 0
    maxOutputDate = ''

    # Alle SNR ID's für Ladungsträger durchlaufen
    for InputID in Input_List:

        # Input-Date für die SNR ID abfragen
        statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = SNR.ID AND o2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE SNR.ID = '"+str(InputID[0])+"' AND MA.MerkmalID = 1"
        cursor.execute(statement)
        InputDate = cursor.fetchone()

        # InputTime-String in Sekunden umwandeln
        InputDateSeconds = convert_from_datestring(InputDate[0][0:-1])

        # Prüfen, ob neues min Input
        if InputDateSeconds < minInputSecond:
            minInputSecond = InputDateSeconds
            minInputDate = InputDate[0]

        # Rückmeldungen zur Input ID abfragen
        statement = "SELECT R.ID FROM Rückmeldung R WHERE R.SNR_ID = "+str(InputID[0])
        cursor.execute(statement)
        Output_List = cursor.fetchall()

        # Alle Rückmeldung ID's durchlaufen
        for OutputID in Output_List:

            # Output-Date für die Rückmeldung ID abfragen
            statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (O2MA.ObjektID = R.ID AND o2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON MA.ID = O2MA.MerkmalsausprägungID WHERE R.ID = '"+str(OutputID[0])+"' AND MA.MerkmalID = 39"
            cursor.execute(statement)
            OutputDate = cursor.fetchone()

            # Falls kein Ergebnis, Schleifendurchlauf verlassen
            if not OutputDate:
                continue
            
            # OutputTime-String in Sekunden umwandeln
            OutputDateSeconds = convert_from_datestring(OutputDate[0][0:-1])

            # Prüfen, ob neues max Output
            if OutputDateSeconds > maxOutputSecond:
                maxOutputSecond = OutputDateSeconds
                maxOutputDate = OutputDate[0]
    
    # Differenz zwischen max und min berechnen
    Dauer = maxOutputSecond - minInputSecond

    if BoxFlag == True:
        BoxTime_List.append(Dauer/3600)

    # Ausgabe
    datei.write("Ladungsträger: "+LagerIn[0]+"        Anzahl: "+str(AnzahlProLad[0])+"        Dauer: "+convert_from_s(Dauer)+"        Start: "+minInputDate[:19]+"         Ende: "+maxOutputDate[:19]+"\n")


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
connection.close()

        


    