import mysql
import mysql.connector
import datetime, time

# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/001Taktung_pro_Artikel/Taktung_pro_Artikel_CSV.txt","w")

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

# Alle Teiltypen abfragen
statement = "SELECT TEIL FROM TEIL ORDER BY TEIL"
cursor.execute(statement)
Teil_List = cursor.fetchall()

# Alle Teiltypen durchlaufen
for Teil in Teil_List:

    # FA des Teiltyps abfragen
    statement = "SELECT SNR.FA FROM SNR WHERE TEIL = '" + Teil[0] + "' GROUP BY SNR.FA ORDER BY SNR.FA"
    cursor.execute(statement)
    FA_List = cursor.fetchall()

    # Ausgabe des Teiltyps mit gefertigter Menge
    datei.write("TEIL:"+ Teil[0] +"\n")
 
    # Alle FA des Teiltyps durchlaufen
    for FA in FA_List:
        
        # Anzahl gefertigter Teile pro FA ermitteln 
        statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
        cursor.execute(statement)
        AnzahlProFA = cursor.fetchone()

        # Alle SNR abfragen, die mehr als einen Input in diesem FA haben
        statement = "SELECT SNR.SNR FROM SNR WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(DISTINCT(ID)) > 1"
        cursor.execute(statement)
        Ausschuss_List = cursor.fetchall()

        minFail = 999
        maxFail = 0
        avgFail = 0

        # Alle SNR, die Ausschuss haben, durchlaufen
        for Ausschuss in Ausschuss_List:

            # Anzahl Input DS für SNR finden in diesem FA
            statement = "SELECT COUNT(*) FROM (SELECT ID FROM SNR WHERE SNR.SNR ='" + Ausschuss[0] + "' AND FA = '" + FA[0] +"') Q"
            cursor.execute(statement)
            AnzahlFail = cursor.fetchone()

            # Ausschuss ist alles mehr als ein Input 
            AnzahlFail = int(AnzahlFail[0])-1

            # Prüfen, ob Ausschuss min oder max darstellt
            if AnzahlFail < minFail:
                minFail = AnzahlFail
            if AnzahlFail > maxFail:
                maxFail = AnzahlFail
            
            # Ausschuss zur AVG-Berechnung hinzufügen
            avgFail = avgFail + AnzahlFail
        

        # Prüfen, ob minFail noch initial ist und ggfls. auf 0 setzen
        if minFail == 999:
            minFail = 0

        # Alle Input ID's abfragen, die einen Output haben, zum FA gehören und SNR != NULL
        statement = "SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.ID"
        cursor.execute(statement)
        SNRID_List = cursor.fetchall()

        # Variablendeklaration pro FA
        minTime = second_min
        maxTime = 0
        avgTime = 0
        avgDifference = 0
        
        # Alle ID's durchlaufen
        for SNRID in SNRID_List:

            # Listdeklaration, in der Dauern (Input DS bis zugehörigem letztem Output DS) einer SNR gespeichert werden
            help_List = list()

            # Input-Zeit der ID abfragen
            statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID WHERE MA.MerkmalID = 1 AND SNR.ID = " + str(SNRID[0])
            cursor.execute(statement)
            InputTime = cursor.fetchone()

            # InputTime-String in Sekunden umwandeln
            InputSecond = convert_from_datestring(InputTime[0][0:-1])

            # Alle Rückmeldung ID's für Input ID abfragen
            statement = "SELECT R.ID FROM Rückmeldung R WHERE SNR_ID = " + str(SNRID[0])
            cursor.execute(statement)
            RID_List = cursor.fetchall()
            
            # Rückmeldung ID's durchlaufen
            for RID in RID_List:

                # Rückmeldung-Zeit der ID abfragen
                statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID WHERE MA.MerkmalID = 39 AND R.ID = " + str(RID[0])
                cursor.execute(statement)
                OutputTime = cursor.fetchone()
                
                # OutputTime-String in Sekunden umwandeln
                OutputSecond = convert_from_datestring(OutputTime[0][0:-1])

                # Dauer in Liste aufnehmen
                help_List.append(OutputSecond-InputSecond)
                
            
            # Liste sortieren, dass die größte Dauer im 0-ten Element steht
            help_List.sort(reverse=True)
            
            # Dauern über 1h aussortieren
            if help_List[0] < 3600:
                # Prüfen, ob Dauer min oder max darstellt
                if help_List[0] < minTime:
                    minTime = help_List[0]
                if help_List[0] > maxTime:
                    maxTime = help_List[0]
                # Dauer zur AVG Berechnung hinzufügen
                avgTime = avgTime + help_List[0]

            # Falls kein Einbezug der Dauer, Anzahl für AVG Berchnung mindern
            else:
                avgDifference = avgDifference + 1 
        

        # Divisor zur AVG Berechnung pro FA
        divisor = len(SNRID_List)-avgDifference

        # Division durch 0 verhindern
        if divisor > 0:
            # AVG-Zeit pro FA in Sekunden
            avgTime = avgTime/divisor
            # AVG-Fail pro FA in Prozent
            avgFail = (avgFail/AnzahlProFA[0])*100
        
        # Ausgabe pro FA
        datei.write("FA:"+ FA[0] +";"+str(AnzahlProFA[0])+";" + str(maxTime) + ";" +str(minTime)+ ";" + str(avgTime) + "\n")

connection.close()
datei.close()





