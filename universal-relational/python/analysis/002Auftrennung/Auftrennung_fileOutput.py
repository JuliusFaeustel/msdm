import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np

import mysql
import mysql.connector
import datetime, time

# Connection zu DB
connection = mysql.connector.connect(host = "127.0.0.1", user = "root", password = "demo", database = "project_2")
cursor = connection.cursor(buffered=True)

def convert_from_s( seconds ): 
    minutes, seconds = divmod(seconds, 60) 
    hours, minutes = divmod(minutes, 60) 
    days, hours = divmod(hours, 24) 
    string = str(int(days))+"T:"+str(int(hours))+"h:"+str(int(minutes))+"m:"+str(int(seconds))+ "s"
    return string

# Ausgabe
datei = open("C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/002Auftrennung/Auftrennung.txt","w")

# Teile
teil_array = ["A","B","C","D","E","F","G","H","I","K"]

# Fertigungszeiten
date_min = datetime.datetime.strptime("2100-12-31T23:59:59.000000", "%Y-%m-%dT%H:%M:%S.%f")
second_min = time.mktime(date_min.timetuple())

# Fertigungszeiten
# Alle FA für ein Teil
i = 0
for teil in teil_array:
    datei.write("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    datei.write("\n")
    datei.write("TEIL: "+ teil_array[i])
    datei.write("\n")

    Anzahl_sum = 0
     
    statement = "SELECT COUNT(*) FROM (SELECT SNR.ID FROM SNR JOIN Rückmeldung R ON SNR.ID = R.SNR_ID WHERE TEIL = '" + teil[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR.SNR) Q"
    cursor.execute(statement)
    Anzahl = cursor.fetchone()
    Anzahl_tmp = int(Anzahl[0])

    statement = "SELECT SNR.SNR FROM SNR WHERE SNR.TEIL = '" + teil[0] + "' AND SNR.SNR IS NOT NULL GROUP BY SNR HAVING COUNT(DISTINCT(ID)) > 1"
    cursor.execute(statement)
    Ausschuss_List = cursor.fetchall()

    min_time = second_min
    max_time = 0
    avg_time = 0
    avg_aus = 0
    avgZeit = 0
    time_list = list()
    count_times = 0

    #alle SNR durchlaufen, die mehrmals vorkommen
    for Ausschuss in Ausschuss_List:
        #ID und Ausprägung der Inputs abfragen, geordnet nach Datum aufsteigend
        statement = "SELECT SNR.ID, MA.Ausprägung from SNR join Objekt2Merkmalsausprägung as O2MA on SNR.ID = O2MA.ObjektID join Merkmalsausprägung as MA on O2MA.MerkmalsausprägungID = MA.ID WHERE O2MA.ObjektTyp = 1 AND SNR = '" + Ausschuss[0] + "' AND MerkmalID = 1 ORDER BY Ausprägung"
        cursor.execute(statement)
        result_in = cursor.fetchall()
        #print(result_in)
        #print('IN:' +str(result_in))
        Anzahl_aus = len(result_in)-1
        #print(Anzahl_aus)
        avg_aus = avg_aus + Anzahl_aus
        #print(avg_aus)

        k = 1
        diff_time = 0
        for res in result_in:
            statement = "SELECT MA.Ausprägung from Rückmeldung R join Objekt2Merkmalsausprägung as O2MA on R.ID = O2MA.ObjektID join Merkmalsausprägung as MA on O2MA.MerkmalsausprägungID = MA.ID WHERE O2MA.ObjektTyp = 2 AND R.SNR_ID = " + str(res[0]) + " AND MerkmalID = 39 ORDER BY Ausprägung DESC"
            #print(statement)
            cursor.execute(statement)
            result_out = cursor.fetchone()
            #print('OUT:'+str(result_out))
            #print('Cursor' + str(cursor.rowcount))
            if not result_out:
                k = k + 1
                continue
            if cursor.rowcount > 0:
                date_old_out = datetime.datetime.strptime(result_out[0][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
                second_old_in = time.mktime(date_old_out.timetuple())
                #print('k: '+str(k))
                #print('LEN: '+str(len(result_in)))
                if k < len(result_in):
                    #print('IN:' +str(result_in[k][1]))
                    date_new_in = datetime.datetime.strptime(result_in[k][1][0:-1], "%Y-%m-%dT%H:%M:%S.%f")
                    second_new_in = time.mktime(date_new_in.timetuple())

                    diff_time = second_new_in - second_old_in
                    #print('DIFF:' + str(diff_time))

                    if diff_time < min_time:
                        min_time = diff_time
                    if diff_time > max_time:
                        max_time = diff_time
                    avg_time = avg_time + diff_time
                    count_times = count_times + 1
                    time_list.append(diff_time/60)
            k = k +1
            #print('K : '+str(k))
                


    if min_time == second_min:
        min_time = 0
        
    if count_times != 0:
        avgZeit = avg_time / count_times
        avg_aus = (avg_aus/Anzahl_tmp)*100
        
    if avgZeit != 0:
        plt.figure(1)
        plt.title('Ausschusszeiten')
        plt.ylabel('Minuten')
        plt.xlabel('Teilart')
        plt.axis
        plt.boxplot(time_list, labels=[teil[0]], showfliers=False, positions=[i+1])
        

    

    #avgZeit_gesamt = avgZeit_gesamt/len(FA_List)
    #avg_aus_gesamt = avg_aus_gesamt/len(FA_List)
    datei.write("MIN: " +convert_from_s(min_time)+ "        MAX: " +convert_from_s(max_time)+ "        AVG: " + convert_from_s(avgZeit)+ "      Ausschussfaktor: " +str(format(avg_aus, '.2f'))+" %\n")
    i = i + 1

plt.savefig('C:/Users/picht/Desktop/Projektseminar I-490/universell-relational/Ergebnisse/002Auftrennung/boxplots/Ausschuss.png')
plt.close(1)
datei.close()
        



