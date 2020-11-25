import mysql
import mysql.connector
import datetime, time

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor()

# Teile
teil_array = ["A","B","C","D","E","F","G","H","I","K"]

# Summe der Teile
sumTeil_array = []

# Anzahl gefertigter TEILE ermitteln
for teil in teil_array:
    statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE TEIL = '" + teil + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
    cursor.execute(statement)
    result = cursor.fetchone()
    sumTeil_array.append(result[0])

#print(sumTeil_array)

# Fertigungszeiten
date_min = datetime.datetime.strptime("2100-12-31T23:59:59.000000", "%Y-%m-%dT%H:%M:%S.%f")
second_min = time.mktime(date_min.timetuple())

# Fertigungszeiten
# Alle FA für ein Teil
i = 0
for teil in teil_array:
    statement = "SELECT SNR.FA FROM SNR WHERE TEIL = '" + teil + "' GROUP BY SNR.FA ORDER BY SNR.FA"
    cursor.execute(statement)
    FA_List = cursor.fetchall()
    print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    print("\n")
    print("TEIL: "+ teil_array[i] + "       Gesamtanzahl gefertigt: "+ str(sumTeil_array[i])+"\n")
    print("\n")

         
    j = 0
    Anzahl_sum = 0
    for FA in FA_List:
        statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
        cursor.execute(statement)
        Anzahl = cursor.fetchone()
        Anzahl_tmp = int(Anzahl[0])

        statement = "SELECT SNR.SNR FROM SNR WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(DISTINCT(ID)) > 1"
        cursor.execute(statement)
        Ausschuss_List = cursor.fetchall()

        min_aus = second_min
        max_aus = 0
        avg_aus = 0

        for Ausschuss in Ausschuss_List:
            statement = "SELECT ID FROM SNR WHERE SNR.SNR ='" + Ausschuss[0] + "'"
            cursor.execute(statement)
            result_aus = cursor.fetchall()
            Anzahl_aus = len(result_aus)-1
            if Anzahl_aus < min_aus:
                min_aus = Anzahl_aus
            if Anzahl_aus > max_aus:
                max_aus = Anzahl_aus
            avg_aus = avg_aus + Anzahl_aus

        if min_aus == second_min:
            min_aus = 0
        
        statement = "SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE SNR.FA = '" + FA[0] + "' AND SNR.SNR IS NOT NULL"
        cursor.execute(statement)
        SNR_List = cursor.fetchall()

        minZeit = second_min
        maxZeit = 0
        avgZeit = 0
        avg_diff = 0
        for SNR in SNR_List:
            help_array = []
            # Input-Zeit
            statement = "SELECT Ausprägung FROM SNR JOIN Objekt2Merkmalsausprägung O2MA ON (SNR.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 1) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID WHERE MA.MerkmalID = 1 AND SNR.ID = " + str(SNR[0])
            cursor.execute(statement)
            result = cursor.fetchone()
            date_in = datetime.datetime.strptime(result[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
            second_in = time.mktime(date_in.timetuple())

            # alle passenden R.ID suchen
            statement = "SELECT R.ID FROM Rückmeldung R WHERE SNR_ID = " + str(SNR[0])
            #print(statement)
            cursor.execute(statement)
            RID_List = cursor.fetchall()
            
            # passenden R.ID durchlaufen
            for RID in RID_List:
                # Output-Zeit
                statement = "SELECT Ausprägung FROM Rückmeldung R JOIN Objekt2Merkmalsausprägung O2MA ON (R.ID = O2MA.ObjektID AND O2MA.ObjektTyp = 2) JOIN Merkmalsausprägung MA ON O2MA.MerkmalsausprägungID = MA.ID WHERE MA.MerkmalID = 39 AND R.ID = " + str(RID[0])
                #print(statement)
                #print(row2[0])
                cursor.execute(statement)
                result_RA = cursor.fetchone()
                #print(result_RA)
                date_out = datetime.datetime.strptime(result_RA[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
                second_out = time.mktime(date_out.timetuple())
                help_array.append(second_out-second_in)
                
            
                help_array.sort(reverse=True)
                #print("HELP")
                #print(help_array)
                if help_array[0] < 3600:
                    if help_array[0] < minZeit:
                        minZeit = help_array[0]
                    if help_array[0] > maxZeit:
                        maxZeit = help_array[0]
                    avgZeit = avgZeit + help_array[0]
                else:
                    avg_diff = avg_diff + 1 
        

        if len(SNR_List) > 0:
            #print(len(SNR_List))
            #print(avg_diff)
            divisor = len(SNR_List)-avg_diff
            avgZeit = avgZeit/divisor
            avg_aus = (avg_aus/Anzahl_tmp)*100
        
        
        print("FA: "+ FA_List[j][0] +"     Anzahl gefertigt: "+str(Anzahl_tmp)+"        MIN: " +str(format(minZeit/60, '.2f'))+ " min        MAX: " +str(format(maxZeit/60, '.2f'))+ " min        AVG: " + str(format(avgZeit/60, '.2f'))+ " min     MIN_FAIL: " + str(min_aus)+ "       MAX_FAIL: " + str(max_aus)+"        AVG_FAIL: "+str(format(avg_aus, '.2f'))+" %\n")
        Anzahl_sum = Anzahl_sum + Anzahl_tmp
        #print(Anzahl_sum)
        j = j + 1
    i = i + 1
        




