import pyodbc
import datetime, time

# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mssql_new/Ergebnisse/001Taktung_pro_Artikel/Taktung_pro_Artikel.txt","w")
dateiCSV = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/mssql_new/Ergebnisse/001Taktung_pro_Artikel/Taktung_pro_Artikel.csv","w")

dateiCSV.write("TEIL;FA;COUNT;MIN;MAX;AVG\n")

# Verbindung zu DB aufbauen
server = 'DESKTOP-0IJEV10\\SQLEXPRESS'
database = 'project_3'
username = 'paul'
password = '123'

connection = pyodbc.connect(driver = '{ODBC Driver 17 for SQL Server}', server = server , database = database, UID = username, PWD = password)
cursor = connection.cursor()

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
Teil_List = cursor.fetchall()

# Alle Teiltypen durchlaufen
for Teil in Teil_List:

    # FA des Teiltyps abfragen
    statement = "SELECT SNR.FA FROM SNR WHERE TEIL = '" + Teil[0] + "' GROUP BY SNR.FA ORDER BY SNR.FA"
    cursor.execute(statement)
    FA_List = cursor.fetchall()

    # Alle FA des Teiltyps durchlaufen
    for FA in FA_List:

        # Anzahl gefertigter Teile pro FA ermitteln 
        statement = "SELECT COUNT(*) FROM (SELECT DISTINCT(SNR.SNR) FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL) Q"
        cursor.execute(statement)
        AnzahlProFA = cursor.fetchone()

        statement = "SELECT SNR.ID, MA.Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON (O2M.ObjektID = SNR.ID AND O2M.ObjektTyp = 1) JOIN Merkmal M ON O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID WHERE M.ID = 1 AND SNR.FA ='" + FA[0] +"'"
        cursor.execute(statement)
        Input_List = cursor.fetchall()
        
        str1 = ''
        for ele in Input_List:  
            str1 = str1 + str(ele[0]) + ','
        str1 = str1[:-1]

        statement = "SELECT R.SNR_ID, MAX(MA.Ausprägung) FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON ((R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2)) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID JOIN Objekt2Merkmal O2M ON ((O2M.ObjektID = R.ID AND O2M.ObjektTyp = 2)) JOIN Merkmal M ON O2M.MerkmalID = M.ID AND M.ID = MA.MerkmalID WHERE M.ID = 39 AND R.SNR_ID IN ("+ str1 +") GROUP BY R.SNR_ID"
        cursor.execute(statement)
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
        statement = "SELECT SNR.SNR FROM SNR WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(ID) > 1"
        cursor.execute(statement)
        AusschussSNR_List = cursor.fetchall()

        str2 = ''
        for ele2 in AusschussSNR_List:  
            str2 = str2 + str(ele2[0]) + ','
        str2 = str2[:-1]

        if str2 != '':
            statement = "SELECT COUNT(ID), SNR FROM SNR WHERE FA = '" + FA[0] + "' AND SNR IN ("+ str2 +") GROUP BY SNR.SNR"
            cursor.execute(statement)
            Ausschuss_List = cursor.fetchall()

            maxFail = max(Ausschuss_List)[0]-1
            minFail = min(Ausschuss_List)[0]-1
            sumFail = 0
            for i in range(len(Ausschuss_List)):
                sumFail = sumFail + Ausschuss_List[i][0] - 1

            avgFail = (sumFail/AnzahlProFA[0])*100

        # Ausgabe pro FA
        datei.write("FA: "+ FA[0] +"     Anzahl gefertigt: "+str(AnzahlProFA[0])+"        MIN: " + convert_from_s(minTime) + "        MAX: " +convert_from_s(maxTime)+ "        AVG: " + convert_from_s(avgTime) + "     MIN_FAIL: " + str(minFail)+ "       MAX_FAIL: " + str(maxFail)+"        AVG_FAIL: "+str(format(avgFail, '.2f'))+" %\n")
        dateiCSV.write(Teil[0] +";"+ FA[0] +";"+ str(AnzahlProFA[0]) +";"+ str(format(minTime, '.2f')) +";"+ str(format(maxTime, '.2f')) +";"+ str(format(avgTime, '.2f')) +"\n")
           
datei.close()
dateiCSV.close()
connection.close()




        

